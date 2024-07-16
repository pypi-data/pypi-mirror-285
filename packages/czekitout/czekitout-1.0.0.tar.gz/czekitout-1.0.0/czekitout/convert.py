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
r"""Contains functions that facilitate type-conversions with useful error
messages when exceptions are thrown.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For performing deep copies.
import copy



# For general array handling.
import numpy as np



# For type-checking objects.
import czekitout.isa

# For validating objects.
import czekitout.check



##################################
## Define classes and functions ##
##################################

# List of public objects in objects.
__all__ = ["to_dict",
           "to_str_from_str_like",
           "to_single_dim_slice",
           "to_multi_dim_slice",
           "to_list_of_strs",
           "to_tuple_of_strs",
           "to_float",
           "to_int",
           "to_bool",
           "to_positive_float",
           "to_nonnegative_float",
           "to_nonnegative_int",
           "to_positive_int",
           "to_list_of_ints",
           "to_tuple_of_ints",
           "to_list_of_positive_ints",
           "to_tuple_of_positive_ints",
           "to_list_of_nonnegative_ints",
           "to_tuple_of_nonnegative_ints",
           "to_list_of_floats",
           "to_tuple_of_floats",
           "to_list_of_positive_floats",
           "to_tuple_of_positive_floats",
           "to_list_of_nonnegative_floats",
           "to_tuple_of_nonnegative_floats",
           "to_pair_of_floats",
           "to_pair_of_positive_floats",
           "to_pair_of_nonnegative_floats",
           "to_pair_of_ints",
           "to_pair_of_positive_ints",
           "to_pair_of_nonnegative_ints",
           "to_quadruplet_of_nonnegative_ints",
           "to_pairs_of_floats",
           "to_pairs_of_ints",
           "to_pairs_of_nonnegative_ints",
           "to_real_two_column_numpy_matrix",
           "to_numpy_array",
           "to_real_numpy_array",
           "to_real_numpy_array_1d",
           "to_real_numpy_matrix",
           "to_real_numpy_array_3d",
           "to_nonnegative_numpy_array",
           "to_nonnegative_numpy_matrix",
           "to_bool_numpy_matrix",
           "to_bool_numpy_array_3d",
           "to_complex_numpy_array",
           "to_complex_numpy_matrix"]



def to_dict(obj, obj_name):
    r"""Convert input object to an instance of the class `dict`.

    If the input object is not dictionary-like, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be dictionary-like.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if type(obj) is dict:
        result = obj
    else:
        czekitout.check.if_dict_like(obj, obj_name)
        result = dict(obj)

    return result



def to_str_from_str_like(obj, obj_name):
    r"""Convert string-like input object to an instance of the class `str`.

    If the input object is not string-like, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be an instance of the class `str` or
        `bytes`.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    If the input object is an instance of the class `bytes`, then said object is
    decoded to an instance of the class `str` via ``obj.decode("utf-8")``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `str`
        The object resulting from the conversion.

    """
    czekitout.check.if_str_like(obj, obj_name)

    result = (np.array(obj).tolist().decode("utf-8")
              if (type(np.array(obj).tolist()) is bytes)
              else str(np.array(obj).tolist()))

    return result



def to_single_dim_slice(obj, obj_name):
    r"""Convert a one-dimensional slice-like input object to a one-dimensional 
    slice object.

    We define a one-dimensional slice-like object as any object that is an 
    integer, a sequence of integers, or a `slice` object.

    We define a one-dimensional slice object as any object that is an integer, a
    `list` of integers, or a `slice` object.

    If the input object is not one-dimensional slice-like, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be an integer, a sequence of integers, or
        a `slice` object.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `str`
        The object resulting from the conversion.

    """
    czekitout.check.if_single_dim_slice_like(obj, obj_name)

    if isinstance(obj, slice):
        result = copy.deepcopy(obj)
    else:
        try:
            convert_to_list_of_ints = to_list_of_ints  # Alias for readability.
            result = convert_to_list_of_ints(obj, obj_name)
        except:
            convert_to_int = to_int  # Alias for readability.
            result = convert_to_int(obj, obj_name)
    
    return result



def to_multi_dim_slice(obj, obj_name):
    r"""Convert a multi-dimensional slice-like input object to a 
    multi-dimensional slice object.

    We define a multi-dimensional slice-like object as a sequence of items which
    contains at most one item being a sequence of integers, and the remaining
    items being `slice` objects and/or integers.

    We define a multi-dimensional slice object as a `tuple` of items which
    contains at most one item being a `list` of integers, and the remaining
    items being `slice` and/or `int` objects.

    If the input object is not multi-dimensional slice-like, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of items which contains at 
        most one item being a sequence of integers, and the remaining items 
        being `slice` objects and/or integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `str`
        The object resulting from the conversion.

    """
    czekitout.check.if_multi_dim_slice_like(obj, obj_name)
    result = list(obj)

    for idx, single_dim_slice in enumerate(obj):
        # Alias for readability.
        convert_to_single_dim_slice = to_single_dim_slice

        result[idx] = convert_to_single_dim_slice(single_dim_slice,
                                                  "single_dim_slice")

    result = tuple(result)
    
    return result



def to_list_of_strs(obj, obj_name):
    r"""Convert input object to a list of strings.

    If the input object is not a sequence of string-like objects, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a sequence, where each element in the
        sequence is an instance of the class `str` or `bytes`.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_str_like_seq(obj, obj_name)

    convert_to_str_from_str_like = \
        to_str_from_str_like  # Alias for readability.
    
    result = list(convert_to_str_from_str_like(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_strs(obj, obj_name):
    r"""Convert input object to a tuple of strings.

    If the input object is not a sequence of string-like objects, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a sequence, where each element in the
        sequence is an instance of the class `str` or `bytes`.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_strs = to_list_of_strs  # Alias for readability.
    result = tuple(convert_to_list_of_strs(obj, obj_name))

    return result



def to_float(obj, obj_name):
    r"""Convert input object to a `float`.

    If the input object is not a real number, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be a real number.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        convert_to_str_from_str_like = \
            to_str_from_str_like  # Alias for readability.

        intermediate_conversion_of_obj = obj

        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_str_from_str_like(**kwargs)

        if intermediate_conversion_of_obj == "True":
            result = 1.0
        elif intermediate_conversion_of_obj == "False":
            result = 0.0
        else:
            intermediate_conversion_of_obj = \
                complex(intermediate_conversion_of_obj)
            
            kwargs["obj"] = intermediate_conversion_of_obj
            czekitout.check.if_float(**kwargs)
            result = intermediate_conversion_of_obj.real
    except:
        try:
            intermediate_conversion_of_obj = \
                complex(np.array(intermediate_conversion_of_obj).tolist())
            
            kwargs["obj"] = intermediate_conversion_of_obj
            czekitout.check.if_float(**kwargs)
            result = intermediate_conversion_of_obj.real
        except:
            kwargs["obj"] = intermediate_conversion_of_obj
            czekitout.check.if_float(**kwargs)

    return result



def to_int(obj, obj_name):
    r"""Convert input object to an `int`.

    If the input object is not an integer, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be an integer.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj

        convert_to_float = to_float  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_float(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_int(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_int(**kwargs)
        
    result = round(intermediate_conversion_of_obj)

    return result



def to_bool(obj, obj_name):
    r"""Convert input object to a `bool`.

    If the input object is not a boolean, then a `TypeError` exception is raised
    with the message::

        The object ``<obj_name>`` must be boolean.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj
        
        convert_to_int = to_int  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_int(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_bool(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_bool(**kwargs)

    result = bool(intermediate_conversion_of_obj)

    return result



def to_positive_float(obj, obj_name):
    r"""Convert input object to a positive `float`.

    If the input object is not a positive real number, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a positive real number.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a real number, otherwise said
    exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj
        
        convert_to_float = to_float  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_float(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_positive_float(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_positive_float(**kwargs)
    
    result = intermediate_conversion_of_obj

    return result



def to_nonnegative_float(obj, obj_name):
    r"""Convert input object to a nonnegative `float`.

    If the input object is not a nonnegative real number, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a nonnegative real number.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a real number, otherwise said
    exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj
        
        convert_to_float = to_float  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_float(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_nonnegative_float(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_nonnegative_float(**kwargs)
        
    result = intermediate_conversion_of_obj

    return result



def to_nonnegative_int(obj, obj_name):
    r"""Convert input object to a nonnegative `int`.

    If the input object is not a nonnegative integer, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a nonnegative integer.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not an integer, otherwise said exception
    is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj
        
        convert_to_int = to_int  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_int(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_nonnegative_int(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_nonnegative_int(**kwargs)
        
    result = intermediate_conversion_of_obj

    return result



def to_positive_int(obj, obj_name):
    r"""Convert input object to a positive `int`.

    If the input object is not a positive integer, then an exception is raised
    with the message::

        The object ``<obj_name>`` must be a positive integer.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not an integer, otherwise said exception
    is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    try:
        intermediate_conversion_of_obj = obj
        
        convert_to_int = to_int  # Alias for readability.
        kwargs = {"obj": intermediate_conversion_of_obj, "obj_name": obj_name}
        intermediate_conversion_of_obj = convert_to_int(**kwargs)

        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_positive_int(**kwargs)
    except:
        kwargs["obj"] = intermediate_conversion_of_obj
        czekitout.check.if_positive_int(**kwargs)
        
    result = intermediate_conversion_of_obj

    return result



def to_list_of_ints(obj, obj_name):
    r"""Convert input object to a list of `int` objects.

    If the input object is not a sequence of integers, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_int_seq(obj, obj_name)

    convert_to_int = to_int  # Alias for readability.

    result = list(convert_to_int(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_ints(obj, obj_name):
    r"""Convert input object to a tuple of `int` objects.

    If the input object is not a sequence of integers, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """

    convert_to_list_of_ints = to_list_of_ints  # Alias for readability.
    result = tuple(convert_to_list_of_ints(obj, obj_name))

    return result



def to_list_of_positive_ints(obj, obj_name):
    r"""Convert input object to a list of positive integers.

    If the input object is not a sequence of positive integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of positive integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of integers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_positive_int_seq(obj, obj_name)
    
    convert_to_int = to_int  # Alias for readability.

    result = list(convert_to_int(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_positive_ints(obj, obj_name):
    r"""Convert input object to a tuple of positive integers.

    If the input object is not a sequence of positive integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of positive integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of integers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_positive_ints = \
        to_list_of_positive_ints  # Alias for readability.
    result = \
        tuple(convert_to_list_of_positive_ints(obj, obj_name))

    return result



def to_list_of_nonnegative_ints(obj, obj_name):
    r"""Convert input object to a list of nonnegative integers.

    If the input object is not a sequence of nonnegative integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of nonnegative integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of integers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_nonnegative_int_seq(obj, obj_name)

    convert_to_int = to_int  # Alias for readability.

    result = list(convert_to_int(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_nonnegative_ints(obj, obj_name):
    r"""Convert input object to a tuple of nonnegative integers.

    If the input object is not a sequence of nonnegative integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of nonnegative integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of integers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_nonnegative_ints = \
        to_list_of_nonnegative_ints  # Alias for readability.
    result = \
        tuple(convert_to_list_of_nonnegative_ints(obj, obj_name))

    return result



def to_list_of_floats(obj, obj_name):
    r"""Convert input object to a list of floating-point numbers.

    If the input object is not a sequence of real numbers, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a sequence of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_float_seq(obj, obj_name)

    convert_to_float = to_float  # Alias for readability.

    result = list(convert_to_float(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_floats(obj, obj_name):
    r"""Convert input object to a tuple of floating-point numbers.

    If the input object is not a sequence of real numbers, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_floats = to_list_of_floats  # Alias for readability.
    result = tuple(convert_to_list_of_floats(obj, obj_name))

    return result



def to_list_of_positive_floats(obj, obj_name):
    r"""Convert input object to a list of positive floating-point numbers.

    If the input object is not a sequence of positive real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of positive real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_positive_float_seq(obj, obj_name)

    convert_to_float = to_float  # Alias for readability.

    result = list(convert_to_float(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_positive_floats(obj, obj_name):
    r"""Convert input object to a tuple of positive floating-point numbers.

    If the input object is not a sequence of positive real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of positive real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_positive_floats = \
        to_list_of_positive_floats  # Alias for readability.
    result = \
        tuple(convert_to_list_of_positive_floats(obj, obj_name))

    return result



def to_list_of_nonnegative_floats(obj, obj_name):
    r"""Convert input object to a list of nonnegative floating-point numbers.

    If the input object is not a sequence of nonnegative real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of nonnegative real
        numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_nonnegative_float_seq(obj, obj_name)

    convert_to_float = to_float  # Alias for readability.

    result = list(convert_to_float(elem_of_obj, "elem_of_obj")
                  for elem_of_obj
                  in obj)

    return result



def to_tuple_of_nonnegative_floats(obj, obj_name):
    r"""Convert input object to a tuple of nonnegative floating-point numbers.

    If the input object is not a sequence of nonnegative real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of nonnegative real
        numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    convert_to_list_of_nonnegative_floats = \
        to_list_of_nonnegative_floats  # Alias for readability.
    result = \
        tuple(convert_to_list_of_nonnegative_floats(obj, obj_name))

    return result



def to_pair_of_floats(obj, obj_name):
    r"""Convert input object to a two-element tuple of `float` objects.

    If the input object is not a pair of real numbers, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a pair of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_floats(obj, obj_name)

    convert_to_tuple_of_floats = to_tuple_of_floats  # Alias for readability.
    result = convert_to_tuple_of_floats(obj, obj_name)

    return result



def to_pair_of_positive_floats(obj, obj_name):
    r"""Convert input object to a two-element tuple of positive `float` objects.

    If the input object is not a pair of positive real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a pair of positive real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a pair of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_positive_floats(obj, obj_name)
    
    convert_to_tuple_of_floats = to_tuple_of_floats  # Alias for readability.
    result = convert_to_tuple_of_floats(obj, obj_name)

    return result



def to_pair_of_nonnegative_floats(obj, obj_name):
    r"""Convert input object to a two-element tuple of nonnegative `float` 
    objects.

    If the input object is not a pair of nonnegative real numbers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a pair of nonnegative real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a pair of real numbers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_nonnegative_floats(obj, obj_name)

    convert_to_tuple_of_floats = to_tuple_of_floats  # Alias for readability.
    result = convert_to_tuple_of_floats(obj, obj_name)

    return result



def to_pair_of_ints(obj, obj_name):
    r"""Convert input object to a two-element tuple of `int` objects.

    If the input object is not a pair of integers, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be a pair of integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_ints(obj, obj_name)

    convert_to_tuple_of_ints = to_tuple_of_ints  # Alias for readability.    
    result = convert_to_tuple_of_ints(obj, obj_name)

    return result



def to_pair_of_positive_ints(obj, obj_name):
    r"""Convert input object to a two-element tuple of positive `int` objects.

    If the input object is not a pair of positive integers, then an exception
    is raised with the message::

        The object ``<obj_name>`` must be a pair of positive integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a pair of integers, otherwise said
    exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_positive_ints(obj, obj_name)

    convert_to_tuple_of_ints = to_tuple_of_ints  # Alias for readability.    
    result = convert_to_tuple_of_ints(obj, obj_name)

    return result



def to_pair_of_nonnegative_ints(obj, obj_name):
    r"""Convert input object to a two-element tuple of non-negative `int` 
    objects.

    If the input object is not a pair of non-negative integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a pair of non-negative integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a pair of integers, otherwise said
    exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pair_of_nonnegative_ints(obj, obj_name)

    convert_to_tuple_of_ints = to_tuple_of_ints  # Alias for readability.    
    result = convert_to_tuple_of_ints(obj, obj_name)

    return result



def to_quadruplet_of_nonnegative_ints(obj, obj_name):
    r"""Convert input object to a four-element tuple of non-negative `int` 
    objects.

    If the input object is not a quadruplet of non-negative integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a quadruplet of non-negative integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a quadruplet of integers, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_quadruplet_of_nonnegative_ints(obj, obj_name)

    convert_to_tuple_of_ints = to_tuple_of_ints  # Alias for readability.    
    result = convert_to_tuple_of_ints(obj, obj_name)

    return result



def to_pairs_of_floats(obj, obj_name):
    r"""Convert input object to a tuple of two-element tuples of `float` 
    objects.

    If the input object is not a sequence of pairs of real numbers, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of pairs of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pairs_of_floats(obj, obj_name)

    convert_to_pair_of_floats = to_pair_of_floats  # Alias for readability.
    result = tuple(convert_to_pair_of_floats(elem_of_obj, "elem_of_obj")
                   for elem_of_obj
                   in obj)

    return result



def to_pairs_of_ints(obj, obj_name):
    r"""Convert input object to a tuple of two-element tuples of `int` objects.

    If the input object is not a sequence of pairs of integers, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of pairs of integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. 

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pairs_of_ints(obj, obj_name)

    convert_to_pair_of_ints = to_pair_of_ints  # Alias for readability.
    result = tuple(convert_to_pair_of_ints(elem_of_obj, "elem_of_obj")
                   for elem_of_obj
                   in obj)

    return result



def to_pairs_of_nonnegative_ints(obj, obj_name):
    r"""Convert input object to a tuple of two-element tuples of nonnegative 
    integers.

    If the input object is not a sequence of pairs of nonnegative integers, then
    an exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of pairs of nonnegative
        integers.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a sequence of pairs of integers,
    otherwise said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    czekitout.check.if_pairs_of_nonnegative_ints(obj, obj_name)

    convert_to_pair_of_ints = to_pair_of_ints  # Alias for readability.
    result = tuple(convert_to_pair_of_ints(elem_of_obj, "elem_of_obj")
                   for elem_of_obj
                   in obj)

    return result



def to_real_two_column_numpy_matrix(obj, obj_name):
    r"""Convert input object to a real-valued 2D two-column numpy array.

    If the input object is not a real-valued two-column matrix, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a be a two-column matrix of real 
        numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    err_msg = _to_real_two_column_numpy_matrix_err_msg_1.format(obj_name)
    
    if czekitout.isa.real_two_column_numpy_matrix(obj):
        result = obj
    else:
        try:
            result = np.array(obj)
            kwargs = {"obj": result, "obj_name": obj_name}
            czekitout.check.if_real_two_column_numpy_matrix(**kwargs)
        except:
            raise TypeError(err_msg)

    return result



def to_numpy_array(obj, obj_name):
    r"""Convert input object to a numpy array.

    If the input object is not an array, then a `TypeError` exception is raised
    with the message::

        The object ``<obj_name>`` must be an array.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.numpy_array(obj):
        result = obj
    else:
        try:
            result = np.array(obj)
        except:
            err_msg = _to_numpy_array_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_real_numpy_array(obj, obj_name):
    r"""Convert input object to a real-valued numpy array.

    If the input object is not a real-valued array, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be a real-valued array.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.real_numpy_array(obj):
        result = obj
    else:
        try:
            intermediate_conversion_of_obj = np.array(obj)
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_real_numpy_array(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except:
            err_msg = _to_real_numpy_array_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_real_numpy_array_1d(obj, obj_name):
    r"""Convert input object to a real-valued 1D numpy array.

    If the input object is not a real-valued 1D array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be real-valued 1D array.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.real_numpy_array_1d(obj):
        result = obj
    else:
        try:
            intermediate_conversion_of_obj = np.array(obj)
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_real_numpy_array_1d(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except:
            err_msg = _to_real_numpy_array_1d_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_real_numpy_matrix(obj, obj_name):
    r"""Convert input object to a real-valued numpy array.

    If the input object is not a real-valued matrix, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be real-valued matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.real_numpy_matrix(obj):
        result = obj
    else:
        try:
            intermediate_conversion_of_obj = np.array(obj)
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_real_numpy_matrix(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except:
            err_msg = _to_real_numpy_matrix_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_real_numpy_array_3d(obj, obj_name):
    r"""Convert input object to a real-valued 3D numpy array.

    If the input object is not a real-valued 3D matrix, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be real-valued 3D matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.real_numpy_array_3d(obj):
        result = obj
    else:
        try:
            intermediate_conversion_of_obj = np.array(obj)
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_real_numpy_array_3d(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except:
            err_msg = _to_real_numpy_array_3d_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_nonnegative_numpy_array(obj, obj_name):
    r"""Convert input object to a nonnegative numpy array.

    If the input object is not a nonnegative array, then an exception is raised
    with the message::

        The object ``<obj_name>`` must be nonnegative array.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a numpy array of real numbers,
    otherwise said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.nonnegative_numpy_array(obj):
        result = obj
    else:
        err_msg = _to_nonnegative_numpy_array_err_msg_1.format(obj_name)

        try:
            intermediate_conversion_of_obj = np.array(obj)
        except:
            raise TypeError(err_msg)

        try:
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_nonnegative_numpy_array(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except ValueError:
            raise ValueError(err_msg)
        except BaseException:
            raise TypeError(err_msg)

    return result



def to_nonnegative_numpy_matrix(obj, obj_name):
    r"""Convert input object to a nonnegative numpy matrix.

    If the input object is not a nonnegative matrix, then an exception is raised
    with the message::

        The object ``<obj_name>`` must be nonnegative matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a numpy matrix of real numbers,
    otherwise said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.nonnegative_numpy_matrix(obj):
        result = obj
    else:
        err_msg = _to_nonnegative_numpy_matrix_err_msg_1.format(obj_name)

        try:
            intermediate_conversion_of_obj = np.array(obj)
        except:
            raise TypeError(err_msg)
        
        try:
            kwargs = {"obj": intermediate_conversion_of_obj,
                      "obj_name": obj_name}
            czekitout.check.if_nonnegative_numpy_matrix(**kwargs)
            result = np.array(intermediate_conversion_of_obj, dtype=float)
        except ValueError:
            raise ValueError(err_msg)
        except BaseException:
            raise TypeError(err_msg)

    return result



def to_bool_numpy_matrix(obj, obj_name):
    r"""Convert input object to a boolean 2D numpy array.

    If the input object is not a boolean 2D matrix, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be boolean matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.bool_numpy_matrix(obj):
        result = obj
    else:
        czekitout.check.if_bool_matrix(obj, obj_name)
        result = np.array(obj, dtype=bool)

    return result



def to_bool_numpy_array_3d(obj, obj_name):
    r"""Convert input object to a boolean 3D numpy array.

    If the input object is not a boolean 3D matrix, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be 3D boolean matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.bool_numpy_array_3d(obj):
        result = obj
    else:
        czekitout.check.if_bool_array_3d(obj, obj_name)
        result = np.array(obj, dtype=bool)

    return result



def to_complex_numpy_array(obj, obj_name):
    r"""Convert input object to a complex-valued numpy array.

    If the input object is not a complex-valued array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a complex-valued array.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.complex_numpy_array(obj):
        result = obj
    else:
        try:
            result = np.array(obj, dtype=complex)
            kwargs = {"obj": result, "obj_name": obj_name}
            czekitout.check.if_complex_numpy_array(**kwargs)
        except:
            err_msg = _to_complex_numpy_array_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



def to_complex_numpy_matrix(obj, obj_name):
    r"""Convert input object to a complex-valued numpy array.

    If the input object is not a complex-valued matrix, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be complex-valued matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    Returns
    -------
    result : `dict`
        The object resulting from the conversion.

    """
    if czekitout.isa.complex_numpy_matrix(obj):
        result = obj
    else:
        try:
            result = np.array(obj, dtype=complex)
            kwargs = {"obj": result, "obj_name": obj_name}
            czekitout.check.if_complex_numpy_matrix(result, obj_name)
        except:
            err_msg = _to_complex_numpy_matrix_err_msg_1.format(obj_name)
            raise TypeError(err_msg)

    return result



###########################
## Define error messages ##
###########################

_to_real_two_column_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be two-column matrix of real numbers.")

_to_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be an array.")

_to_real_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a real-valued array.")

_to_real_numpy_array_1d_err_msg_1 = \
    ("The object ``{}`` must be a real-valued 1D array.")

_to_real_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a real-valued matrix.")

_to_real_numpy_array_3d_err_msg_1 = \
    ("The object ``{}`` must be a real-valued 3D array.")

_to_nonnegative_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a nonnegative array.")

_to_nonnegative_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a nonnegative matrix.")

_to_complex_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a complex-valued array.")

_to_complex_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a complex-valued matrix.")
