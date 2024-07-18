# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Externs
# =======

cdef extern from "c_get_config.h":

    cdef bint is_use_symmetry() nogil
    cdef bint is_use_openmp() nogil
    cdef bint is_count_perf() nogil
    cdef bint is_use_loop_unrolling() nogil
    cdef bint is_debug_mode() nogil
    cdef bint is_cython_build_in_source() nogil
    cdef bint is_cython_build_for_doc() nogil
    cdef bint is_use_long_int() nogil
    cdef bint is_use_unsigned_long_int() nogil
