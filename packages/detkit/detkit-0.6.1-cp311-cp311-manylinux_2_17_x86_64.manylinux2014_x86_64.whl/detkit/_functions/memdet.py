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

import signal
import numpy
from .memory import Memory
from ._memdet_util import signal_handler
from ._memdet_io import initialize_io, cleanup_mem
from ._ansi import ANSI
from .._openmp import get_avail_num_threads
import time
from ..__version__ import __version__
from ._utilities import get_processor_name
from ._memdet_gen import memdet_gen
from ._memdet_sym import memdet_sym
from ._memdet_spd import memdet_spd

__all__ = ['memdet']

# Register signal handler for SIGINT (Ctrl+C) and SIGTSTP (Ctrl+Z)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)


# ====================
# pivot to permutation
# ====================

def _pivot_to_permutation(piv):
    """
    Convert pivot of indices to permutation of indices.
    """

    perm = numpy.arange(len(piv))
    for i in range(len(piv)):
        perm[i], perm[piv[i]] = perm[piv[i]], perm[i]

    return perm


# ======
# memdet
# ======

def memdet(
        A,
        num_blocks=1,
        assume='gen',
        triangle=None,
        mixed_precision='float64',
        parallel_io=None,
        scratch_dir=None,
        overwrite=False,
        return_info=False,
        verbose=False):
    """
    Compute log-determinant under memory constraint.

    Parameters
    ----------

    A : numpy.ndarray or numpy.memmap or zarr.core.Array
        Square non-singular matrix.

    num_blocks : int, default=1
        Number of memory blocks along rows and columns.

        * If `=1`:  the whole matrix is loaded to memory as one block. No
          scratchpad disk space is needed as all data is on memory.
        * If `=2`:  matrix is decomposed to 2 by 2 memory blocks (four blocks),
          but three of these blocks will be loaded concurrently to memory. No
          scratchpad disk space is needed.
        * If `>2`: matrix is decomposed to a grid of (``num_blocks``,
          ``num_blocks``) blocks, but only `4` of these blocks will be loaded
          concurrently. Scratchpad disk space will be created (see
          ``scratch_dir`` option).

        The number of blocks  may or may not be a divisor of the matrix size.
        If the number of blocks is not a divisor of the matrix size, the blocks
        on the last row-block and column-block will have smaller size.

    triangle : ``'l'``, ``'u'``, or None, default=None
        When the  matrix is symmetric, this option indicates whether the full
        matrix is stored or only half triangle part of the matrix is given.

        * ``'l'``: assumes the lower-triangle part of the matrix is given.
        * ``'u'``: assumes the upper-triangle part of the matrix is given.
        * ``None``: indicates full matrix is given.

    assume : str {``'gen'``, ``'sym'``, ``'spd'``}, default=``'gen'``
        Assumption on the input matrix `A`:

        * ``'gen'``: generic square matrix
        * ``'sym'``: symmetric matrix
        * ``'spd'``: symmetric positive-definite matrix

    mixed_precision : str {``'float32'``, ``'float64'``}, or numpy.dtype,\
            default= ``'float64'``
        The precision at which the computations are performed. This may be
        different than the data type of the input  matrix. It is recommended
        to set a precision higher than the dtype of the input matrix. For
        instance, if the input matrix has ``float32`` data type, you may
        set this option to ``float64``.

    parallel_io : str {``'mp'``, ``'dask'``, ``'ts'``} or None, default=None
        Parallel data transfer (load and store operations) from memory to
        scratchpad on the disk and vice-versa:

        * ``'mp'``: utilizes Python's built-in multiprocessing.
        * ``'dask'``: utilizes Dask's multiprocessing. For this to work,
          the package `dask <https://www.dask.org/>`__ should be installed.
        * ``'ts'``: utilizes TensorStore's multiprocessing. For this to work,
          the packages
          `tensorstore <https://google.github.io/tensorstore/>`__ and
          `zarr <https://zarr.readthedocs.io/>`__ should be installed.
        * ``None``: no parallel processing is performed. All data transfer is
          performed on a single CPU thread.

        .. note::

            The option ``'ts'`` can only be used when the input matrix `A` is
            a `zarr` array. See `zarr <https://zarr.readthedocs.io/>`__
            package.

    scratch_dir : str, default=None
        When ``num_blocks`` is greater than `2`, the computations are performed
        on a scratchpad space on disk. This option determines the directory
        where memdet should create a temporary scratch file. If ``None``, the
        default OS's tmp directory will be used. For instance, in UNIX, this is
        almost always ``'/tmp'`` directory.

        .. note::

            This directory should have enough space as much as the size of the
            input matrix (or half of the input matrix size if ``triangle``
            option is set).

    overwrite : boolean, default=True
        Uses the input matrix storage as scratchpad space. The overwrites the
        input matrix.

    return_info : bool, default=False
        Returns a dictionary containing profiling information such as wall and
        process time, memory allocation, disk usage, etc. See ``info`` variable
        in the return section below.

    verbose : bool, default=False
        Prints verbose output during computation.

    Returns
    -------

    ld : float
        :math:`\\mathrm{logabsdet}(\\mathbf{A})`, which is the natural
        logarithm of the absolute value of the determinant of the input matrix.
    sign : int
        Sign of determinant
    diag : numpy.array
        An array of the size of the number rows (or columns) of the matrix,
        containing the diagonal elements of the matrix decomposition as
        follows:

        * For genetic matrix (when ``assume='gen'``), this is the diagonal
          entries of the matrix :math:`\\mathbf{U}` in the LU decomposition
          :math:`\\mathbf{P} \\mathbf{A} = \\mathbf{L} \\mathbf{U}`.
        * For symmetric matrix (when ``assume='sym'``), this is the diagonal
          entries of the matrix :math:`\\mathbf{D}` in the LDL decomposition
          :math:`\\mathbf{P} \\mathbf{A} = \\mathbf{U}^{\\intercal}
          \\mathbf{D} \\mathbf{U}` where :math:`\\mathbf{U}` is
          upper-triangular.
        * For symmetric positive-definite matrix (when ``assume='spd'``), this
          is the diagonal entries of the matrix :math:`\\mathbf{L}` in the
          Cholesky decomposition :math:`\\mathbf{A} = \\mathbf{U}^{\\intercal}
          \\mathbf{U}` where :math:`\\mathbf{U}` is upper-triangular.

    if ``return_info=True``:

        info : dict
            A dictionary containing the following key-values:

            * ``'matrix'``: info about input matrix
                * ``'dtype'``: the data type of the input matrix.
                * ``'matrix_shape'``: shape of the input matrix.
                * ``'triangle'``: in case of symmetric matrix, whether upper
                  or lower triangle part of matrix is given (based on
                  ``triangle`` option).
                * ``'assume'``: whether matrix is generic, symmetric, or
                  symmetric and positive-definite (based on ``assume`` option).
            * ``'process'``: info about the computation process and profiling
                * ``'processor'``: name of the CPU processor
                * ``'tot_wall_time'``: total wall time of the process.
                * ``'tot_proc_time'``: total process time of all CPU threads
                  combined.
                * ``'load_wall_time'``: wall time for only the load operation,
                  which is the data transfer from disk to memory. This is
                  relevant only if scratchpad space was used during the
                  computation.
                * ``'load_proc_time'``: process time of all CPU threads for
                  only the load operation, which is the data transfer from disk
                  to memory. This is relevant only if scratchpad space was
                  used during the computation.
                * ``'store_wall_time'``: wall time for only the store
                  operation, which is the data transfer from memory to disk.
                  This is relevant only if scratchpad space was used during the
                  computation.
                * ``'store_proc_time'``: process time of all CPU threads for
                  only the store operation, which is the data transfer from
                  memory to disk. This is relevant only if scratchpad space was
                  used during the computation.
            * ``'block'``: info about matrix blocks
                * ``'block_nbytes'``: number of bytes of each block allocated
                  on the memory. When the number of blocks along row-block (or
                  column-block) is not a divisor of the matrix size, some
                  blocks may be smaller, however, this quantity reports the
                  size of the largest block.
                * ``'block_shape'``: shape of each memory block in array size.
                  When the number of blocks along row-block (or column-block)
                  is not a divisor of the matrix size, some blocks may be
                  smaller, however, this quantity reports the size of the
                  largest block.
                * ``'matrix_blocks'``: the shape of the grid of blocks that
                  decomposes the input matrix, which is (``num_blocks``,
                  ``num_blocks``).
            * ``'scratch'``: info about scratchpad space (relevant if used)
                * ``'io_chunk'``: the size of data chunks for for input/output
                  data transfer operations between disk and memory. This size
                  is almost always equal to the size of number of rows/columns
                  of each block (see ``block_shape`` above).
                * ``'num_scratch_blocks'``: number of blocks stored to the
                  scratchpad space. Note that not all memory blocks are
                  stored, hence, this quantity is smaller than
                  ``num_blocks * num_blocks``.
                * ``'scratch_file'``: the scratch file that was created, and
                  later deleted after termination of the algorithm. This file
                  was in the ``scratch_dir`` and it was a hidden file (for
                  instance, in UNIX, it has a dot prefix).
                * ``'scratch_nbytes'``: the size of scratchpad file in bytes.
                * ``'num_block_loads'``: a counter of the number of times
                  that blocks were read from disk to memory.
                * ``'num_block_stores'``: a counter of the number of times
                  that blocks were written from memory to disk.
            * ``'memory'``: info about memory allocation
                * ``'alloc_mem'``: block memory allocated in bytes divided by
                  ``mem_unit``.
                * ``'alloc_mem_peak'``: block peak memory allocated in bytes
                  divided by ``mem_unit``.
                * ``'total_mem'``: total memory allocated in bytes divided by
                  ``mem_unit``. This includes the memory of blocks and any
                  extra memory required by the algorithm.
                * ``'total_mem_peak'``: total peak memory allocated in bytes
                  divided by ``mem_unit``. This includes the memory of blocks
                  and any extra memory required by the algorithm.
                * ``'mem_unit'``: the unit in which the above memory are
                  reported with. This is usually the memory (in bytes) of one
                  block, so it makes the above memory memory sizes relative
                  to the memory size of one block.
            * ``'solver'``: info about the solver
                * ``'version'``: version of detkit package
                * ``'method'``: method of computation, such as LU decomposition
                  , LDL decomposition, or Cholesky decomposition, respectively
                  for generic, symmetric, or symmetric positive-definite
                  matrices.
                * ``'dtype'``: the data type used during computation (see
                  ``'mixed_precision'`` option).
                * ``'order'``: order of array, such as ``C`` for contiguous
                  (row-major) ordering or ``F`` for Fortran (column-major)
                  ordering during computation.

    See also
    --------

    detkit.logdet
    detkit.loggdet
    detkit.logpdet

    Notes
    -----

    for dask, make sure to use if-clause protection
    https://pytorch.org/docs/stable/notes/windows.html
    #multiprocessing-error-without-if-clause-protection

    Examples
    --------

    **Using a zarr array:**

    .. code-block:: python
        :emphasize-lines: 15, 16, 17

        >>> # Create a symmetric matrix
        >>> import numpy
        >>> n = 10000
        >>> A = numpy.random.randn(n, n)
        >>> A = A.T @ A

        >>> # Store matrix as a zarr array on disk (optional)
        >>> import zarr
        >>> z_path = 'my_matrix.zarr'
        >>> z = zarr.open(z_path, mode='w', shape=(n, n), dtype=A.dtype)
        >>> z[:, :] = A

        >>> # Compute log-determinant
        >>> from detkit import memdet
        >>> ld, sign, diag, info = memdet(
        ...         z, num_blocks=3, assume='sym', parallel_io='ts',
        ...         verbose=True, return_info=True)

        >>> # print log-determinant and sign
        >>> print(f'log-abs-determinant: {ld}, sign-determinant: {sign}')
        82104.567748, -1

    The above code also produces the following verbose output:

    .. image:: ../_static/images/plots/memdet_verbose.png
        :align: center
        :class: custom-dark

    Printing the ``info`` variable

    .. code-block:: python

        >>> # Print info results
        >>> from pprint import pprint
        >>> print('%f, %d' % (ld, sign))
        >>> pprint(info)

    .. literalinclude:: ../_static/data/memdet_return_info.txt
        :language: python
    """

    # Initialize time and set memory counter
    mem = Memory()
    mem.set()
    init_wall_time = time.time()
    init_proc_time = time.process_time()

    io = initialize_io(A, num_blocks, assume, triangle, mixed_precision,
                       parallel_io, scratch_dir, verbose=verbose)

    # Track memory up to this point
    alloc_mem = mem.now()
    alloc_mem_peak = mem.peak()

    # Main algorithm
    try:

        # Main log-determinant computation
        if assume == 'gen':
            # Generic matrix, using LU decomposition
            ld, sign, diag = memdet_gen(io, verbose)

        elif assume == 'sym':
            # Symmetric matrix, using LDL decomposition
            ld, sign, diag = memdet_sym(io, verbose)

        elif assume == 'spd':
            # Symmetric positive-definite matrix, using Cholesky decomposition
            ld, sign, diag = memdet_spd(io, verbose)

        else:
            raise ValueError('"assume" should be either "gen", "sym", or ' +
                             '"spd".')

    except Exception as e:
        print(f'{ANSI.RESET}{ANSI.BR_RED}{ANSI.BOLD}failed{ANSI.RESET}',
              flush=True)
        raise e

    except KeyboardInterrupt as e:
        print(f'{ANSI.RESET}', flush=True)
        raise e

    finally:

        # Record time
        tot_wall_time = time.time() - init_wall_time
        tot_proc_time = time.process_time() - init_proc_time

        # Clean allocated memory blocks
        cleanup_mem(io, verbose)

        # Record total memory consumption since start
        total_mem = mem.now()
        total_mem_peak = mem.peak()

    if return_info:

        # method
        if assume == 'gen':
            method = 'lu decomposition'
        elif assume == 'sym':
            method = 'ldl decomposition'
        elif assume == 'spd':
            method = 'cholesky decomposition'
        else:
            raise ValueError('"assume" is invalid.')

        # Get config for info dictionary
        dtype = io['config']['dtype']
        order = io['config']['order']
        n = io['config']['n']
        m = io['config']['m']
        block_nbytes = io['config']['block_nbytes']

        # Info dictionary
        info = {
            'matrix': {
                'dtype': str(A.dtype),
                'matrix_shape': (n, n),
                'triangle': triangle,
                'assume': assume,
            },
            'process': {
                'processor': get_processor_name(),
                'num_proc': get_avail_num_threads(),
                'tot_wall_time': tot_wall_time,
                'tot_proc_time': tot_proc_time,
                'load_wall_time': io['profile']['load_wall_time'],
                'load_proc_time': io['profile']['load_proc_time'],
                'store_wall_time': io['profile']['store_wall_time'],
                'store_proc_time': io['profile']['store_proc_time'],
            },
            'block': {
                'block_nbytes': block_nbytes,
                'block_shape': (m, m),
                'matrix_blocks': (num_blocks, num_blocks),
            },
            'scratch': {
                'io_chunk': io['data']['io_chunk'],
                'num_scratch_blocks': io['config']['num_scratch_blocks'],
                'scratch_file': io['dir']['scratch_file'],
                'scratch_nbytes': io['dir']['scratch_nbytes'],
                'num_block_loads': io['profile']['num_block_loads'],
                'num_block_stores': io['profile']['num_block_stores'],
            },
            'memory': {
                'alloc_mem': alloc_mem / block_nbytes,
                'alloc_mem_peak': alloc_mem_peak / block_nbytes,
                'total_mem': total_mem / block_nbytes,
                'total_mem_peak': total_mem_peak / block_nbytes,
                'mem_unit': '%d bytes' % block_nbytes,
            },
            'solver': {
                'version': __version__,
                'method': method,
                'dtype': str(dtype),
                'order': order,
            }
        }

        return ld, sign, diag, info

    else:
        return ld, sign, diag
