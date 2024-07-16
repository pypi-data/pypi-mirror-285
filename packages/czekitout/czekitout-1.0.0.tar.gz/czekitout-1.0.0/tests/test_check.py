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
r"""Contains tests for the module :mod:`czekitout.convert`.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For general array handling.
import numpy as np

# For operations related to unit tests.
import pytest



# For validating objects.
import czekitout.check



##################################
## Define classes and functions ##
##################################



def test_1_of_if_instance_of_any_accepted_types():
    func_to_test = czekitout.check.if_instance_of_any_accepted_types

    unformatted_err_msgs = \
        (czekitout.check._check_accepted_types_err_msg_1,
         czekitout.check._check_accepted_types_err_msg_1,
         czekitout.check._if_instance_of_any_accepted_types_err_msg_1,
         czekitout.check._if_instance_of_any_accepted_types_err_msg_2,
         czekitout.check._if_instance_of_any_accepted_types_err_msg_2)

    objs = 2*([1, 2], np.random.default_rng(), tuple, 3)
    
    accepted_type_sets = ((list,),
                          (np.random._generator.Generator,),
                          (type, int),
                          (3, None),
                          tuple(),
                          (np.random.RandomState,),
                          [int, float],
                          (str, list, type))

    obj_names = tuple("obj_"+str(idx+1) for idx in range(len(objs)))

    format_arg_sets = \
        (("accepted_types", "type"),
         ("accepted_types", "type"),
         (obj_names[5], "numpy.random.mtrand.RandomState"),
         (obj_names[6], str(("int", "float")).replace("\'", "`")),
         (obj_names[7], str(("str", "list", "type")).replace("\'", "`")))

    for obj_idx, _ in enumerate(objs):
        kwargs = {"obj": objs[obj_idx],
                  "obj_name": obj_names[obj_idx],
                  "accepted_types": accepted_type_sets[obj_idx]}
        if obj_idx <= 2:
            assert func_to_test(**kwargs) == None
        else:
            args = format_arg_sets[obj_idx-3]
            err_msg = unformatted_err_msgs[obj_idx-3].format(*args)
            with pytest.raises(TypeError) as err_info:
                func_to_test(**kwargs)
            assert str(err_info.value) == err_msg
            
    return None



def test_1_of_if_one_of_any_accepted_strings():
    func_to_test = czekitout.check.if_one_of_any_accepted_strings

    unformatted_err_msgs = \
        (czekitout.check._if_str_like_err_msg_1,
         czekitout.check._if_str_like_seq_err_msg_1,
         czekitout.check._if_one_of_any_accepted_strings_err_msg_1,
         czekitout.check._if_one_of_any_accepted_strings_err_msg_2,
         czekitout.check._if_one_of_any_accepted_strings_err_msg_3)

    std_str_1 = "foo"
    std_str_2 = "bar"
    std_str_3 = "foobar"

    byte_str_1 = bytes(std_str_1, "utf-8")
    numpy_byte_str_1 = np.array(byte_str_1)

    objs = (std_str_1, byte_str_1, 3, std_str_1) + 3*(std_str_3,)
    
    accepted_string_sets = ((byte_str_1, std_str_2),
                            (numpy_byte_str_1, std_str_2),
                            (std_str_1, std_str_2),
                            (3, std_str_2),
                            tuple(),
                            (std_str_1,),
                            (std_str_1, std_str_2))

    obj_names = tuple("obj_"+str(idx+1) for idx in range(len(objs)))

    format_arg_sets = ((obj_names[2],),
                       ("accepted_strings",),
                       ("accepted_strings",),
                       (obj_names[5], std_str_1),
                       (obj_names[6], str((std_str_1, std_str_2))))

    for obj_idx, _ in enumerate(objs):
        kwargs = {"obj": objs[obj_idx],
                  "obj_name": obj_names[obj_idx],
                  "accepted_strings": accepted_string_sets[obj_idx]}
        if obj_idx <= 1:
            assert func_to_test(**kwargs) == None
        else:
            args = format_arg_sets[obj_idx-2]
            expected_exception = (TypeError if (obj_idx <= 3) else ValueError)
            err_msg = unformatted_err_msgs[obj_idx-2].format(*args)
            with pytest.raises(expected_exception) as err_info:
                func_to_test(**kwargs)
            assert str(err_info.value) == err_msg
            
    return None



def test_1_of_if_complex_numpy_array():
    func_to_test = czekitout.check.if_complex_numpy_array

    obj_name = "obj"

    complex_two_column_numpy_matrix = (np.random.rand(5, 2)
                                       + 1j*np.random.rand(5, 2))
    real_two_column_numpy_matrix = complex_two_column_numpy_matrix.real
    pairs_of_complex_numbers = complex_two_column_numpy_matrix.tolist()
    pairs_of_real_numbers = real_two_column_numpy_matrix.tolist()

    kwargs = {"obj": complex_two_column_numpy_matrix, "obj_name": obj_name}
    expected_result = None
    assert func_to_test(**kwargs) == expected_result

    kwargs = {"obj": real_two_column_numpy_matrix, "obj_name": obj_name}
    expected_exception = TypeError
    with pytest.raises(expected_exception) as err_info:
        func_to_test(**kwargs)

    kwargs = {"obj": pairs_of_complex_numbers, "obj_name": obj_name}
    expected_exception = TypeError
    with pytest.raises(expected_exception) as err_info:
        func_to_test(**kwargs)

    kwargs = {"obj": pairs_of_real_numbers, "obj_name": obj_name}
    expected_exception = TypeError
    with pytest.raises(expected_exception) as err_info:
        func_to_test(**kwargs)

    return None



def test_1_of_if_callable():
    func_to_test = czekitout.check.if_callable

    unformatted_err_msg_1 = czekitout.check._check_obj_name_err_msg_1
    unformatted_err_msg_2 = czekitout.check._if_callable_err_msg_1

    obj_name = "obj"

    err_msg_1 = unformatted_err_msg_1.format("obj_name", "str")
    err_msg_2 = unformatted_err_msg_2.format(obj_name)

    kwargs = {"obj": max, "obj_name": obj_name}
    expected_result = None
    assert func_to_test(**kwargs) == expected_result

    kwargs = {"obj": "_".join, "obj_name": obj_name}
    expected_result = None
    assert func_to_test(**kwargs) == expected_result

    kwargs = {"obj": max, "obj_name": None}
    expected_exception = TypeError
    expected_err_msg = err_msg_1
    with pytest.raises(expected_exception) as err_info:
        func_to_test(**kwargs)
    assert str(err_info.value) == expected_err_msg

    kwargs = {"obj": 3, "obj_name": obj_name}
    expected_exception = TypeError
    expected_err_msg = err_msg_2
    with pytest.raises(expected_exception) as err_info:
        func_to_test(**kwargs)
    assert str(err_info.value) == expected_err_msg

    return None



###########################
## Define error messages ##
###########################
