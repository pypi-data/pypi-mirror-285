#! /usr/bin/env python

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

import numpy
from detkit import memdet
import zarr
import os
import shutil

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# ==========
# remove dir
# ==========

def remove_dir(dir_name):
    """
    Removes a directory
    """

    if os.path.exists(dir_name):
        try:
            shutil.rmtree(dir_name)
            print('File %s is deleted.' % dir_name)
        except OSError:
            pass

    else:
        print('Directory %s does not exists.' % dir_name)


# ===========
# test memdet
# ===========

def test_memdet():
    """
    Test `memdet` function.
    """

    # Create a symmetric matrix
    n = 1000
    A = numpy.random.randn(n, n)
    A = A.T @ A

    # Store matrix as a zarr array on disk (optional)
    z_path = 'my_matrix.zarr'
    z = zarr.open(z_path, mode='w', shape=(n, n), dtype=A.dtype)
    z[:, :] = A

    # Compute log-determinant
    ld, sign, diag, info = memdet(
            z, num_blocks=3, assume='sym', parallel_io='ts',
            verbose=True, return_info=True)

    # print log-determinant and sign
    print(f'log-abs-determinant: {ld}, sign-determinant: {sign}')

    remove_dir(z_path)


# ===========
# script main
# ===========

if __name__ == "__main__":
    test_memdet()
