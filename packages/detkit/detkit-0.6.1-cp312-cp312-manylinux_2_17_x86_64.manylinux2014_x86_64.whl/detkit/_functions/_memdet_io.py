# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import os
import numpy
import dask
import zarr
import tensorstore
import tempfile
import inspect
import shutil
from multiprocessing import shared_memory
from ._ansi import ANSI
from ._utilities import human_readable_mem
from .memory import Memory
from .disk import Disk
from .._openmp import get_avail_num_threads


__all__ = ['initialize_io', 'cleanup_mem']


# ==================
# get scratch prefix
# ==================

def _get_scratch_prefix():
    """
    Prefix for filename of scratch space. The prefix is the combination of
    package name and function name.
    """

    # Get the name of caller function
    stack = inspect.stack()
    caller_frame = stack[1]
    caller_function_name = caller_frame.function

    # Get the name of package
    frame = inspect.currentframe()
    module_name = frame.f_globals['__name__']
    package_name = module_name.split('.')[0]

    # scratch space filename prefix
    prefix = '.' + package_name + '-' + caller_function_name + '-'

    return prefix


# =============
# find io chunk
# =============

def _find_io_chunk(m):
    """
    Find best io chunk that is a divisor to m.
    """

    # Settings
    preferred_io_chunk = 5000
    max_io_chunk = 15000

    # Find all divisors of m
    divisors = []
    for i in range(1, int(m**0.5) + 1):
        if m % i == 0:
            divisors.append(i)
            if i != m // i:
                divisors.append(m // i)

    # Find the divisor closest to a the preferred chunk size
    io_chunk = min(divisors, key=lambda x: abs(x - preferred_io_chunk))

    if io_chunk > max_io_chunk:
        io_chunk = preferred_io_chunk

    return io_chunk


# =============
# initialize io
# =============

def initialize_io(A, num_blocks, assume, triangle, mixed_precision,
                  parallel_io, scratch_dir, verbose=False):
    """
    Initialize the io dictionary.
    """

    n = A.shape[0]
    if mixed_precision is not None:
        dtype = mixed_precision
    else:
        dtype = A.dtype
    order = 'F'

    # Initialize
    temp_file = None
    temp_dir = None
    scratch = None
    scratch_file = ''
    scratch_nbytes = 0
    num_scratch_blocks = 0
    dask_scratch = None
    ts_scratch = None
    dask_A = None
    ts_A = None
    cached = None
    A11 = None
    A12 = None
    A21_t = None
    A22 = None

    # Block size
    m = (n + num_blocks - 1) // num_blocks

    # Find io_chunk to be a divisor or block size, m
    io_chunk = _find_io_chunk(m)

    if verbose:
        print(f'{ANSI.FAINT}Config:{ANSI.RESET}\n' +
              f'matrix size : {n}\n' +
              f'num blocks  : {num_blocks}x{num_blocks}\n' +
              f'block size  : {m}x{m}\n' +
              f'dtype       : {str(dtype)}\n',
              flush=True)

    block_nbytes = numpy.dtype(dtype).itemsize * (m**2)
    block_hr_nbytes = human_readable_mem(block_nbytes, pad=False)
    if parallel_io == 'mp':
        A11 = shared_memory.SharedMemory(create=True, size=block_nbytes)
    else:
        A11 = numpy.empty((m, m), dtype=dtype, order=order)

    if verbose:
        mem_info = Memory.info()
        mem_avail_hr = human_readable_mem(mem_info.available, pad=False)
        mem_tot_hr = human_readable_mem(mem_info.total, pad=False)
        print(f'{ANSI.FAINT}Memory: {ANSI.RESET}\n' +
              f'total memory        : {mem_tot_hr:>8}\n' +
              f'available memory    : {mem_avail_hr:>8}', flush=True)
        print(f'allocated block A11 : {ANSI.BOLD}{block_hr_nbytes:>8}' +
              f'{ANSI.RESET}', flush=True)

    # Context for tensorstore
    if parallel_io == 'ts':
        # The "total_bytes_limit" MUST be set to zero, otherwise cache builds
        # up and takes the whole memory on each load operation.
        ts_context = tensorstore.Context({
            'cache_pool': {
                'total_bytes_limit': 0,  # DO NOT change this, read above note.
            },
            'data_copy_concurrency': {
                'limit': get_avail_num_threads(),
            }
        })

    # Create dask for input data
    if parallel_io == 'dask':
        if isinstance(A, zarr.core.Array):
            dask_A = dask.array.from_zarr(A, chunks=(io_chunk, io_chunk))
        else:
            dask_A = dask.array.from_array(A, chunks=(io_chunk, io_chunk))
    elif parallel_io == 'ts':

        if isinstance(A, zarr.core.Array):
            spec_1 = {
                'driver': 'zarr',
                'kvstore': {
                    'driver': 'file',
                    'path': A.store.path,
                }
            }

            ts_A = tensorstore.open(spec_1, context=ts_context).result()
        else:
            raise RuntimeError('The "ts" parallel io can be used only for ' +
                               'zarr arrays.')

    if num_blocks > 1:

        if parallel_io == 'mp':
            A12 = shared_memory.SharedMemory(create=True, size=block_nbytes)
            A21_t = shared_memory.SharedMemory(create=True, size=block_nbytes)
        else:
            A12 = numpy.empty((m, m), dtype=dtype, order=order)
            A21_t = numpy.empty((m, m), dtype=dtype, order=order)

        if verbose:
            print(f'allocated block A12 : {ANSI.BOLD}{block_hr_nbytes:>8}' +
                  f'{ANSI.RESET}', flush=True)
            print(f'allocated block A21 : {ANSI.BOLD}{block_hr_nbytes:>8}' +
                  f'{ANSI.RESET}', flush=True)

        if num_blocks > 2:

            # Scratch blocks and size
            if assume == 'gen':
                num_scratch_blocks = num_blocks * (num_blocks - 1) - 1
            elif assume in ['sym', 'spd']:
                num_scratch_blocks = num_blocks * (num_blocks - 1) // 2 + \
                    (num_blocks - 1) - 1
            expected_scratch_nbytes = num_scratch_blocks * block_nbytes
            expected_scratch_hr_nbytes = human_readable_mem(
                expected_scratch_nbytes, pad=False)

            if parallel_io == 'mp':
                A22 = shared_memory.SharedMemory(create=True,
                                                 size=block_nbytes)
            else:
                A22 = numpy.empty((m, m), dtype=dtype, order=order)

            if verbose:
                print(f'allocated block A22 : {ANSI.BOLD}' +
                      f'{block_hr_nbytes:>8}{ANSI.RESET}', flush=True)

            # Scratch space to hold temporary intermediate blocks
            if parallel_io == 'mp':

                # Temporary file as scratch space
                temp_file = tempfile.NamedTemporaryFile(
                        prefix=_get_scratch_prefix(), suffix='.npy',
                        delete=True, dir=scratch_dir)
                scratch_file = temp_file.name

                scratch = numpy.memmap(temp_file.name, dtype=dtype, mode='w+',
                                       shape=(n, n-m), order=order)

            else:
                # Temporary directory as scratch space
                temp_dir = tempfile.TemporaryDirectory(
                    prefix=_get_scratch_prefix(), suffix='.zarr',
                    dir=scratch_dir)

                scratch_file = temp_dir.name

                scratch = zarr.open(temp_dir.name, mode='w', shape=(n, n-m),
                                    dtype=dtype, order=order,
                                    chunks=(io_chunk, io_chunk))

                if parallel_io == 'dask':
                    dask_scratch = dask.array.from_zarr(
                            scratch, chunks=(io_chunk, io_chunk))
                elif parallel_io == 'ts':

                    spec_2 = {
                        'driver': 'zarr',
                        'kvstore': {
                            'driver': 'file',
                            'path': scratch.store.path,
                        }
                    }

                    # Open the Zarr array using tensorstore
                    ts_scratch = tensorstore.open(
                            spec_2, context=ts_context).result()

            # When scratch_dir is None, the tempfile object decides where the
            # scrarch_dir is.
            if scratch_dir is None:
                scratch_dir = os.path.dirname(scratch_file)

            # Check disk space has enough space
            disk_total, _, disk_free = shutil.disk_usage(scratch_dir)
            disk_total_hr = human_readable_mem(disk_total, pad=False)
            disk_free_hr = human_readable_mem(disk_free, pad=False)
            if expected_scratch_nbytes > disk_free:
                raise RuntimeError(
                    'Not enough disk space for scratchpad.' +
                    f'Expecting {expected_scratch_hr_nbytes} disk space.' +
                    f'Available disk space is {disk_free_hr}.')

            if verbose:
                # Get partition info for the scratch directory
                part_info = Disk.partition_info(scratch_dir)

                print(f'\n{ANSI.FAINT}Disk:{ANSI.RESET}\n' +
                      f'filesystem            : {part_info.fstype}\n' +
                      f'device:               : {part_info.device}\n' +
                      f'total disk space      : {disk_total_hr:>8}\n' +
                      f'available disk space  : {disk_free_hr:>8}\n' +
                      f'required scratch size : {ANSI.BOLD}' +
                      f'{expected_scratch_hr_nbytes:>8}{ANSI.RESET}\n' +
                      f'created scratch space : {scratch_file}',
                      flush=True)

            # Cache table flagging which block is moved to scratch space. False
            # means the block is not yet on scratch space, True means it is
            # cached in the scratch space
            cached = numpy.zeros((num_blocks, num_blocks), dtype=bool)

    # Bind all above in a dictionary
    io = {
        'profile': {
            'load_wall_time': 0,
            'load_proc_time': 0,
            'store_wall_time': 0,
            'store_proc_time': 0,
            'num_block_loads': 0,
            'num_block_stores': 0,
        },
        'config': {
            'num_blocks': num_blocks,
            'block_nbytes': block_nbytes,
            'num_scratch_blocks': num_scratch_blocks,
            'n': n,
            'm': m,
            'triangle': triangle,
            'order': order,
            'dtype': dtype,
            'parallel_io': parallel_io,
        },
        'dir': {
            'temp_file': temp_file,
            'temp_dir': temp_dir,
            'scratch_nbytes': scratch_nbytes,
            'scratch_file': scratch_file,
        },
        'data': {
            'io_chunk': io_chunk,
            'scratch': scratch,
            'dask_scratch': dask_scratch,
            'ts_scratch': ts_scratch,
            'dask_A': dask_A,
            'ts_A': ts_A,
            'A': A,
            'cached': cached,
        },
        'arrays': {
            'A11': A11,
            'A12': A12,
            'A21_t': A21_t,
            'A22': A22,
        }
    }

    return io


# ============
# get dir size
# ============

def _get_dir_size(path):
    """
    Get the size of a director.
    """

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


# ===========
# cleanup mem
# ===========

def cleanup_mem(io, verbose):
    """
    Cleanup memory.
    """

    # Unpack dir variables
    temp_file = io['dir']['temp_file']
    temp_dir = io['dir']['temp_dir']
    scratch_nbytes = io['dir']['scratch_nbytes']
    scratch_file = io['dir']['scratch_file']

    # Unpack array variables
    A11 = io['arrays']['A11']
    A12 = io['arrays']['A12']
    A21_t = io['arrays']['A21_t']
    A22 = io['arrays']['A22']

    # Cleanup directory and files
    if temp_file is not None:
        scratch_nbytes = os.path.getsize(scratch_file)
        temp_file.close()
    elif temp_dir is not None:
        scratch_nbytes = _get_dir_size(temp_dir.name)
        temp_dir.cleanup()

        if verbose:
            print('removed scratch space: %s' % scratch_file)

    # Free memory
    if ('A11' in locals()) and isinstance(A11, shared_memory.SharedMemory):
        A11.close()
        A11.unlink

    if ('A12' in locals()) and isinstance(A12, shared_memory.SharedMemory):
        A12.close()
        A12.unlink

    if ('A21_t' in locals()) and \
            isinstance(A21_t, shared_memory.SharedMemory):
        A21_t.close()
        A21_t.unlink

    if ('A22' in locals()) and isinstance(A22, shared_memory.SharedMemory):
        A22.close()
        A22.unlink
