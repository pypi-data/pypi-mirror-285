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
import os
import sys
from ._ansi import ANSI
import numpy
from multiprocessing import shared_memory


__all__ = ['Progress', 'signal_handler', 'get_array', 'get_block_shape']


# ==============
# signal handler
# ==============

def signal_handler(sig, frame):
    """
    Function to handle signals. When Ctrl+Z is pressed, the terminal colors
    still use the ANSI colors that was set during the execution of the code.
    To properly reset the ANSI codes, this function handles the resetting in
    the event of any termination signal.
    """

    if sig == signal.SIGINT:
        print(f'{ANSI.RESET}', flush=True)
        sys.exit(0)

    elif sig == signal.SIGTSTP:
        print(f'{ANSI.RESET}', flush=True)
        os.kill(os.getpid(), signal.SIGSTOP)  # Suspend the process


# ========
# Progress
# ========

class Progress(object):
    """
    Prints memdet progress.
    """

    # ----
    # init
    # ----

    def __init__(self, num_blocks, assume, verbose=False):
        """
        Initialize counter.
        """

        self.verbose = verbose
        self.counter = 0

        if assume == 'gen':

            # Sum of squares from 1 to num_blocks-1
            S1 = (num_blocks-1) * num_blocks * (2*num_blocks-1) // 6

            # Total count
            self.total_count = S1 + num_blocks

        elif assume in ['sym', 'spd']:

            # Sum of squares from 1 to num_blocks-1
            S1 = (num_blocks-1) * num_blocks * (2*num_blocks-1) // 6

            # Sum from 1 to num_blocks-1
            S2 = (num_blocks-1) * num_blocks // 2

            # Total count
            self.total_count = (S1 + S2) // 2 + num_blocks

        else:
            raise ValueError('"assume" should be either "gen", "sym", or ' +
                             '"spd".')

        self.tot_width = len(str(self.total_count))
        self.row_width = len(str(num_blocks))

    # ----------
    # print task
    # ----------

    def print_task(self, k, i, j):
        """
        Prints the task that is going to be processed.
        """

        if self.verbose:

            if (k == 0) and (i == 0) and (j == 0):
                print('', flush=True)

            print(f'{ANSI.FAINT}' +
                  f'processing diag blk: {k+1:>0{self.row_width}d} ' +
                  f'(row blk: {i+1:>0{self.row_width}d}, ' +
                  f'col blk: {j+1:>0{self.row_width}d})' +
                  f'{ANSI.RESET}',
                  flush=True)

    # -----
    # count
    # -----

    def count(self):
        """
        Counts the progress and prints if verbose.
        """

        self.counter += 1
        if self.verbose:
            # print(f'{ANSI.INVERSE}{ANSI.BR_GREEN}{ANSI.BOLD}{ANSI.FAINT}' +
            print(f'{ANSI.BR_BG_GREEN}{ANSI.BOLD}{ANSI.BLACK}' +
                  f'progress: {ANSI.RESET}' +
                  f'{ANSI.BR_BG_GREEN}{ANSI.BOLD}{ANSI.BLACK}' +
                  f'{self.counter:>0{self.tot_width}d}/' +
                  f'{self.total_count:>{self.tot_width}d}{ANSI.RESET}\n',
                  flush=True)


# =========
# get array
# =========

def get_array(shared_mem, shape, dtype, order):
    """
    Get numpy array from shared memory buffer.
    """

    if len(shape) != 2:
        raise ValueError('"shape" should have length of two.')

    if isinstance(shared_mem, shared_memory.SharedMemory):
        # This is shared memory. Return its buffer.
        return numpy.ndarray(shape=shape, dtype=dtype, order=order,
                             buffer=shared_mem.buf)

    else:
        # This is already numpy array. Return itself.
        return shared_mem


# ===============
# get block shape
# ===============

def get_block_shape(block_info, trans=False):
    """
    When m is not a divider of n, the block matrix might not be square, and it
    its shape will depend on the indices i and j of the block.

    Note that the shape of matrix might be smaller than its shape as stored on
    memory, meaning that the intended matrix that we want to work with might be
    a sub-matrix within the block. This function returns the shape of the
    matrix.
    """

    # i and j are the indices of the position of the block within the matrix
    i, j, num_blocks, n = block_info

    # Size of all blocks except the last block
    m = (n + num_blocks - 1) // num_blocks

    # Size of last block
    md = (n-1) % m + 1

    # Shape of block on memory
    block_shape_on_mem = (m, m)

    # Number of rows of the block
    if i == num_blocks - 1:
        m1 = md
    else:
        m1 = m

    # Number of columns of the block
    if j == num_blocks - 1:
        m2 = md
    else:
        m2 = m

    if trans:
        block_shape = (m2, m1)
    else:
        block_shape = (m1, m2)

    return block_shape, block_shape_on_mem
