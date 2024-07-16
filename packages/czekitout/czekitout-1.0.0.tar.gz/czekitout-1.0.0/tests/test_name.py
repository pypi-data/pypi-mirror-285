# -*- coding: utf-8 -*-
# Copyright 2024 Matthew Fitzpatrick.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
r"""Contains tests for the module :mod:`czekitout.name`.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For general array handling.
import numpy as np



# For getting fully qualified class names.
import czekitout.name



##################################
## Define classes and functions ##
##################################



def test_1_of_fully_qualified_class_name():
    module_alias = czekitout.name
    func_alias = module_alias.fully_qualified_class_name

    obj_set = ([1, 2],
               np.random.default_rng(),
               sum)
    expected_result_set = ("list",
                           "numpy.random._generator.Generator",
                           "builtin_function_or_method")
    zip_obj = zip(obj_set, expected_result_set)
    for obj, expected_result in zip_obj:
        assert func_alias(obj) == expected_result

    cls_set = (tuple,
               np.polynomial.polynomial.Polynomial)
    expected_result_set = ("tuple",
                           "numpy.polynomial.polynomial.Polynomial")
    zip_obj = zip(cls_set, expected_result_set)
    for cls, expected_result in zip_obj:
        assert func_alias(cls) == expected_result

    return None



###########################
## Define error messages ##
###########################
