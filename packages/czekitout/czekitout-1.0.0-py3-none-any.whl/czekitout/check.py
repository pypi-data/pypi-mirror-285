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
r"""Contains functions that facilitate validation with useful error messages 
when exceptions are thrown.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# To determine whether an object is path-like.
import os.path
import pathlib



# For general array handling.
import numpy as np



# For getting fully qualified class names.
import czekitout.name

# For type-checking objects.
import czekitout.isa



##################################
## Define classes and functions ##
##################################

# List of public objects in objects.
__all__ = ["if_instance_of_any_accepted_types",
           "if_dict_like",
           "if_str_like",
           "if_str_like_seq",
           "if_one_of_any_accepted_strings",
           "if_float",
           "if_float_seq",
           "if_positive_float",
           "if_positive_float_seq",
           "if_nonnegative_float",
           "if_nonnegative_float_seq",
           "if_int",
           "if_int_seq",
           "if_positive_int",
           "if_positive_int_seq",
           "if_nonnegative_int",
           "if_nonnegative_int_seq",
           "if_single_dim_slice_like",
           "if_multi_dim_slice_like",
           "if_pair_of_floats",
           "if_pair_of_positive_floats",
           "if_pair_of_nonnegative_floats",
           "if_pair_of_ints",
           "if_pair_of_positive_ints",
           "if_pair_of_nonnegative_ints",
           "if_quadruplet_of_nonnegative_ints",
           "if_pairs_of_floats",
           "if_pairs_of_ints",
           "if_pairs_of_nonnegative_ints",
           "if_real_numpy_array",
           "if_real_numpy_array_1d",
           "if_real_numpy_matrix",
           "if_real_two_column_numpy_matrix",
           "if_real_numpy_array_3d",
           "if_nonnegative_numpy_array",
           "if_nonnegative_numpy_matrix",
           "if_bool",
           "if_bool_matrix",
           "if_bool_array_3d",
           "if_complex_numpy_array",
           "if_complex_numpy_matrix",
           "if_callable"]



def _check_obj_name(obj_name):
    accepted_type = str
    
    if type(obj_name) is not accepted_type:
        fully_qualified_class_name = \
            czekitout.name.fully_qualified_class_name # Alias for readability.
        name_of_accepted_type = \
            fully_qualified_class_name(accepted_type)
        err_msg = \
            _check_obj_name_err_msg_1.format("obj_name", name_of_accepted_type)

        raise TypeError(err_msg)

    return None



def _check_accepted_types(accepted_types):
    try:
        if len(tuple(accepted_types)) == 0:
            raise
        isinstance(None, tuple(accepted_types))
    except:
        fully_qualified_class_name = \
            czekitout.name.fully_qualified_class_name # Alias for readability.
        name_of_accepted_type = \
            fully_qualified_class_name(type)
        unformatted_err_msg = \
            _check_accepted_types_err_msg_1
        err_msg = \
            unformatted_err_msg.format("accepted_types", name_of_accepted_type)

        raise TypeError(err_msg)

    return None



def if_instance_of_any_accepted_types(obj, obj_name, accepted_types):
    r"""Check whether input object is one of any given accepted types.

    If the input object is not one of any given accepted type, and
    ``len(accepted_types)=1``, then a `TypeError` exception is raised with the
    message::

        The object ``<obj_name>`` must be instance of the class 
        `<accepted_type>`.

    where <obj_name> is replaced by the contents of the string ``obj_name``, and
    <accepted_type> by the fully qualified class name of ``accepted_types[0]``.

    If the input object is not one of any given accepted type, and
    ``len(accepted_types)>1``, then a `TypeError` exception is raised with the
    message::

        The object ``<obj_name>`` must be instance of one of the following 
        classes: <accepted_types>.

    where <obj_name> is replaced by the contents of the string ``obj_name``, and
    <accepted_types>  by the sequence of the fully qualified class names of the
    accepted types stored in ``accepted_types``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.
    accepted_types : `array_like` (`type`, ndim=1)
        Accepted types.

    """
    _check_obj_name(obj_name)
    _check_accepted_types(accepted_types)

    if not isinstance(obj, tuple(accepted_types)):
        fully_qualified_class_name = \
            czekitout.name.fully_qualified_class_name # Alias for readability.
        names_of_accepted_types = \
            tuple(fully_qualified_class_name(accepted_type)
                  for accepted_type in accepted_types)
                
        if len(names_of_accepted_types) == 1:
            unformatted_err_msg = _if_instance_of_any_accepted_types_err_msg_1
            err_msg = unformatted_err_msg.format(obj_name,
                                                 names_of_accepted_types[0])
        else:
            names_of_accepted_types = \
                str(names_of_accepted_types).replace("\'", "`")
            unformatted_err_msg = _if_instance_of_any_accepted_types_err_msg_2
            err_msg = unformatted_err_msg.format(obj_name,
                                                 names_of_accepted_types)
            
        raise TypeError(err_msg)

    return None



def if_dict_like(obj, obj_name):
    r"""Check whether input object is dictionary-like.

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

    """
    _check_obj_name(obj_name)

    try:
        dict(obj)
    except:
        err_msg = _if_dict_like_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_str_like(obj, obj_name):
    r"""Check whether input object is string-like.

    If the input object is not string-like, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be string-like.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    try:
        obj_as_numpy_array = np.array(obj)
        if ((obj_as_numpy_array.dtype.type is not np.str_)
            and (obj_as_numpy_array.dtype.type is not np.bytes_)):
            obj_as_path = pathlib.Path(obj)
    except:
        err_msg = _if_str_like_err_msg_1.format(obj_name)
        raise TypeError(err_msg)
    
    return None



def if_str_like_seq(obj, obj_name):
    r"""Check whether input object is a sequence of string-like objects.

    If the input object is not a sequence, where each element is string-like,
    then a `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a sequence, where each element is
        string-like.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)
    
    try:
        for elem_of_obj in obj:
            check_if_str_like = if_str_like  # Alias for readability.
            check_if_str_like(elem_of_obj, "elem_of_obj")
    except:
        err_msg = _if_str_like_seq_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_one_of_any_accepted_strings(obj, obj_name, accepted_strings):
    r"""Check whether input object is one of any given accepted strings.

    If the input object is not string-like, then a `TypeError` exception is
    raised with the message::

        The object ``<obj_name>`` must be string-like.

    If ``len(accepted_strings)=1``, and the input object is not the given
    accepted string, then a `ValueError` exception is raised with the message::

        The object ``<obj_name>`` must be set to ``<accepted_string>``.

    where <obj_name> is replaced by the contents of the string ``obj_name``, and
    <accepted_string> by the accepted string.

    If ``len(accepted_strings)>1``, and the input object is not one of any given
    accepted string, then a `ValueError` exception is raised with the message::

        The object ``<obj_name>`` must be set to one of the following strings: 
        ``<accepted_strings>``.

    where <obj_name> is replaced by the contents of the string ``obj_name``, and
    <accepted_strings> by the sequence of strings stored in
    ``accepted_strings``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.
    accepted_strings : `array_like` (`str`, ndim=1)
        Accepted strings.

    """
    check_if_str_like = if_str_like  # Alias for readability.
    check_if_str_like_seq = if_str_like_seq  # Alias for readability.

    _check_obj_name(obj_name)
    check_if_str_like(obj, obj_name)
    check_if_str_like_seq(accepted_strings, "accepted_strings")

    obj_converted_to_std_type = (np.array(obj).tolist().decode("utf-8")
                                 if (type(np.array(obj).tolist()) is bytes)
                                 else str(np.array(obj).tolist()))

    accepted_strings_converted_to_std_types = tuple()
    for accepted_string in accepted_strings:
        if type(np.array(accepted_string).tolist()) is bytes:
            std_str = np.array(accepted_string).tolist().decode("utf-8")
        else:
            std_str = str(np.array(accepted_string).tolist())
        accepted_strings_converted_to_std_types += (std_str,)

    if obj_converted_to_std_type not in accepted_strings_converted_to_std_types:
        if len(accepted_strings) == 0:
            unformatted_err_msg = _if_one_of_any_accepted_strings_err_msg_1
            args = tuple()
        elif len(accepted_strings) == 1:
            unformatted_err_msg = _if_one_of_any_accepted_strings_err_msg_2
            args = (obj_name, accepted_strings_converted_to_std_types[0])
        else:
            unformatted_err_msg = _if_one_of_any_accepted_strings_err_msg_3
            args = (obj_name, str(accepted_strings_converted_to_std_types))
            
        err_msg = unformatted_err_msg.format(*args)            
        raise ValueError(err_msg)

    return None



def if_scalar(obj, obj_name):
    r"""Check whether input object is a scalar.

    We define a scalar as a number that is boolean, an integer, real-valued, or
    complex-valued.

    If the input object is not a scalar, then a `TypeError` exception is raised
    with the message::

        The object ``<obj_name>`` must be a scalar.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    try:
        obj_as_numpy_array = np.array(obj)
        if ((obj_as_numpy_array.dtype.type is not np.str_)
            and (obj_as_numpy_array.dtype.type is not np.bytes_)):
            complex(obj_as_numpy_array.tolist())
        else:
            raise
    except:
        err_msg = _if_scalar_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_float(obj, obj_name):
    r"""Check whether input object is a real number.

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

    """
    _check_obj_name(obj_name)

    try:
        check_if_scalar = if_scalar  # Alias for readability.
        check_if_scalar(obj, obj_name)

        obj_as_complex = complex(np.array(obj).tolist())
        if abs(obj_as_complex.real - obj_as_complex) > 1.0e-14:
            raise
    except:
        err_msg = _if_float_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_float_seq(obj, obj_name):
    r"""Check whether input object is a sequence of real numbers.

    If the input object is not a sequence of real numbers, then an exception
    exception is raised with the message::

        The object ``<obj_name>`` must be a sequence of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    try:
        for elem_of_obj in obj:
            check_if_float = if_float  # Alias for readability.
            check_if_float(elem_of_obj, "elem_of_obj")
    except:
        err_msg = _if_float_seq_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_positive_float(obj, obj_name):
    r"""Check whether input object is a positive real number.

    If the input object is not a positive real number, then an
    exception is raised with the message::

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

    """
    check_if_float = if_float  # Alias for readability.
    check_if_float(obj, obj_name)

    real_part_of_obj = complex(np.array(obj).tolist()).real
    
    if real_part_of_obj <= 0:
        err_msg = _if_positive_float_err_msg_1.format(obj_name)
        raise ValueError(err_msg)

    return None



def if_positive_float_seq(obj, obj_name):
    r"""Check whether input object is a sequence of positive real numbers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_positive_float_seq_err_msg_1.format(obj_name)

        check_if_float_seq = if_float_seq  # Alias for readability.
        check_if_float_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_positive_float = \
                if_positive_float  # Alias for readability.
            
            check_if_positive_float(elem_of_obj, "elem_of_obj")
            
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_nonnegative_float(obj, obj_name):
    r"""Check whether input object is a nonnegative real number.

    If the input object is not a nonnegative real number, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a nonnegative real number.

    where <obj_name> is replaced by the contents of the string ``obj_name``. In
    the case that an exception is raised, said exception is of the type
    `TypeError` if the input object is not a real number, otherwise
    said exception is of the type `ValueError`.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    check_if_float = if_float  # Alias for readability.
    check_if_float(obj, obj_name)

    real_part_of_obj = complex(np.array(obj).tolist()).real
    
    if real_part_of_obj < 0:
        err_msg = _if_nonnegative_float_err_msg_1.format(obj_name)
        raise ValueError(err_msg)

    return None



def if_nonnegative_float_seq(obj, obj_name):
    r"""Check whether input object is a sequence of nonnegative real numbers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_nonnegative_float_seq_err_msg_1.format(obj_name)

        check_if_float_seq = if_float_seq  # Alias for readability.
        check_if_float_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_nonnegative_float = \
                if_nonnegative_float  # Alias for readability.
            
            check_if_nonnegative_float(elem_of_obj, "elem_of_obj")
            
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_int(obj, obj_name):
    r"""Check whether input object is an integer.

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

    """
    _check_obj_name(obj_name)

    try:
        check_if_float = if_float  # Alias for readability.
        check_if_float(obj, obj_name)

        real_part_of_obj = complex(np.array(obj).tolist()).real

        if abs(round(real_part_of_obj) - real_part_of_obj) > 1.0e-14:
            raise
    except:
        err_msg = _if_int_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_int_seq(obj, obj_name):
    r"""Check whether input object is a sequence of integers.

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

    """
    _check_obj_name(obj_name)
    
    try:
        for elem_of_obj in obj:
            check_if_int = if_int  # Alias for readability.
            check_if_int(elem_of_obj, "elem_of_obj")
    except:
        err_msg = _if_int_seq_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_positive_int(obj, obj_name):
    r"""Check whether input object is a positive integer.

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

    """
    check_if_int = if_int  # Alias for readability.
    check_if_int(obj, obj_name)
    
    try:
        real_part_of_obj = complex(np.array(obj).tolist()).real
        if round(real_part_of_obj) < 1:
            raise
    except:
        err_msg = _if_positive_int_err_msg_1.format(obj_name)
        raise ValueError(err_msg)

    return None



def if_positive_int_seq(obj, obj_name):
    r"""Check whether input object is a sequence of positive integers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_positive_int_seq_err_msg_1.format(obj_name)

        check_if_int_seq = if_int_seq  # Alias for readability.
        check_if_int_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_positive_int = if_positive_int  # Alias for readability.
            check_if_positive_int(elem_of_obj, "elem_of_obj")
            
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_nonnegative_int(obj, obj_name):
    r"""Check whether input object is a nonnegative integer.

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

    """
    check_if_int = if_int  # Alias for readability.
    check_if_int(obj, obj_name)
    
    try:
        real_part_of_obj = complex(np.array(obj).tolist()).real
        if round(real_part_of_obj) < 0:
            raise
    except:
        err_msg = _if_nonnegative_int_err_msg_1.format(obj_name)
        raise ValueError(err_msg)

    return None



def if_nonnegative_int_seq(obj, obj_name):
    r"""Check whether input object is a sequence of nonnegative integers.

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

    """
    _check_obj_name(obj_name)
    
    try:
        err_msg = _if_nonnegative_int_seq_err_msg_1.format(obj_name)

        check_if_int_seq = if_int_seq  # Alias for readability.
        check_if_int_seq(obj, obj_name)

        for elem_of_obj in obj:
            # Alias for readability.
            check_if_nonnegative_int = if_nonnegative_int

            check_if_nonnegative_int(elem_of_obj, "elem_of_obj")
            
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_single_dim_slice_like(obj, obj_name):
    r"""Check whether input object is a one-dimensional slice-like object.

    We define a one-dimensional slice-like object as any object that is an 
    integer, a sequence of integers, or a `slice` object.

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

    """
    try:    
        try:
            check_if_int_seq = if_int_seq  # Alias for readability.
            check_if_int_seq(obj, obj_name)
        except:
            if not isinstance(obj, slice):
                check_if_int = if_int  # Alias for readability.
                check_if_int(obj, obj_name)
    except:
        err_msg = _if_single_dim_slice_like_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_multi_dim_slice_like(obj, obj_name):
    r"""Check whether input object is a multi-dimensional slice-like object.

    We define a multi-dimensional slice-like object as a sequence of items which
    contains at most one item being a sequence of integers, and the remaining
    items being `slice` objects and/or integers.

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

    """
    _check_obj_name(obj_name)

    num_single_dim_slices_as_lists = 0
    
    try:
        for elem_of_obj in obj:
            # Alias for readability.
            check_if_single_dim_slice_like = if_single_dim_slice_like

            check_if_single_dim_slice_like(elem_of_obj, "elem_of_obj")

            try:
                check_if_int_seq = if_int_seq  # Alias for readability.
                check_if_int_seq(elem_of_obj, "elem_of_obj")
                num_single_dim_slices_as_lists += 1
            except:
                pass

        if num_single_dim_slices_as_lists > 1:
            raise

    except:
        err_msg = _if_multi_dim_slice_like_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_pair_of_floats(obj, obj_name):
    r"""Check whether input object is a pair of real numbers.

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

    """
    _check_obj_name(obj_name)

    try:
        count = 0
        for elem_of_obj in obj:
            check_if_float = if_float  # Alias for readability.
            check_if_float(elem_of_obj, "elem_of_obj")
            count += 1
        if count != 2:
            raise
    except:
        err_msg = _if_pair_of_floats_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_pair_of_positive_floats(obj, obj_name):
    r"""Check whether input object is a pair of positive real numbers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_pair_of_positive_floats_err_msg_1.format(obj_name)

        count = 0
        for elem_of_obj in obj:
            count += 1
        if count != 2:
            raise

        check_if_float_seq = if_float_seq  # Alias for readability.
        check_if_float_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_positive_float = \
                if_positive_float  # Alias for readability.
            
            check_if_positive_float(elem_of_obj, "elem_of_obj")
        
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_pair_of_nonnegative_floats(obj, obj_name):
    r"""Check whether input object is a pair of nonnegative real numbers.

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

    """
    _check_obj_name(obj_name)
    
    try:
        err_msg = _if_pair_of_nonnegative_floats_err_msg_1.format(obj_name)

        count = 0
        for elem_of_obj in obj:
            count += 1
        if count != 2:
            raise

        check_if_float_seq = if_float_seq  # Alias for readability.
        check_if_float_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_nonnegative_float = \
                if_nonnegative_float  # Alias for readability.
            
            check_if_nonnegative_float(elem_of_obj, "elem_of_obj")
        
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_pair_of_ints(obj, obj_name):
    r"""Check whether input object is a pair of integers.

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

    """
    _check_obj_name(obj_name)

    try:
        count = 0
        for elem_of_obj in obj:
            check_if_int = if_int  # Alias for readability.
            check_if_int(elem_of_obj, "elem_of_obj")
            count += 1
        if count != 2:
            raise
    except:
        err_msg = _if_pair_of_ints_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_pair_of_positive_ints(obj, obj_name):
    r"""Check whether input object is a pair of positive integers.

    If the input object is not a pair of positive integers, then an exception is
    raised with the message::

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_pair_of_positive_ints_err_msg_1.format(obj_name)

        count = 0
        for elem_of_obj in obj:
            count += 1
        if count != 2:
            raise

        check_if_int_seq = if_int_seq  # Alias for readability.
        check_if_int_seq(obj, obj_name)

        for elem_of_obj in obj:
            check_if_positive_int = if_positive_int  # Alias for readability.
            check_if_positive_int(elem_of_obj, "elem_of_obj")
        
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_pair_of_nonnegative_ints(obj, obj_name):
    r"""Check whether input object is a pair of nonnegative integers.

    If the input object is not a pair of nonnegative integers, then an exception
    is raised with the message::

        The object ``<obj_name>`` must be a pair of nonnegative integers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_pair_of_nonnegative_ints_err_msg_1.format(obj_name)

        count = 0
        for elem_of_obj in obj:
            count += 1
        if count != 2:
            raise

        check_if_int_seq = if_int_seq  # Alias for readability.
        check_if_int_seq(obj, obj_name)

        for elem_of_obj in obj:
            # Alias for readability.
            check_if_nonnegative_int = if_nonnegative_int
            check_if_nonnegative_int(elem_of_obj, "elem_of_obj")
        
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_quadruplet_of_nonnegative_ints(obj, obj_name):
    r"""Check whether input object is a quadruplet of nonnegative integers.

    If the input object is not a quadruplet of nonnegative integers, then an
    exception is raised with the message::

        The object ``<obj_name>`` must be a quadruplet of nonnegative integers.

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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_quadruplet_of_nonnegative_ints_err_msg_1.format(obj_name)

        count = 0
        for elem_of_obj in obj:
            count += 1
        if count != 4:
            raise

        check_if_int_seq = if_int_seq  # Alias for readability.
        check_if_int_seq(obj, obj_name)
        
        for elem_of_obj in obj:
            # Alias for readability.
            check_if_nonnegative_int = if_nonnegative_int
            check_if_nonnegative_int(elem_of_obj, "elem_of_obj")
        
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_pairs_of_floats(obj, obj_name):
    r"""Check whether input object is a sequence of pairs of real numbers.

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

    """
    _check_obj_name(obj_name)

    try:
        for elem_of_obj in obj:
            # Alias for readability.
            check_if_pair_of_floats = if_pair_of_floats
            
            check_if_pair_of_floats(elem_of_obj, "elem_of_obj")
            
    except:
        err_msg = _if_pairs_of_floats_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_pairs_of_ints(obj, obj_name):
    r"""Check whether input object is a sequence of pairs of integers.

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

    """
    _check_obj_name(obj_name)
    
    try:
        for elem_of_obj in obj:
            # Alias for readability.
            check_if_pair_of_ints = if_pair_of_ints
            
            check_if_pair_of_ints(elem_of_obj, "elem_of_obj")
            
    except:
        err_msg = _if_pairs_of_ints_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_pairs_of_nonnegative_ints(obj, obj_name):
    r"""Check whether input object is a sequence of pairs of nonnegative 
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

    """
    _check_obj_name(obj_name)

    try:
        err_msg = _if_pairs_of_nonnegative_ints_err_msg_1.format(obj_name)

        check_if_pairs_of_ints = if_pairs_of_ints  # Alias for readability.
        check_if_pairs_of_ints(obj, obj_name)

        for elem_of_obj in obj:
            # Alias for readability.
            check_if_pair_of_nonnegative_ints = if_pair_of_nonnegative_ints
            
            check_if_pair_of_nonnegative_ints(elem_of_obj, "elem_of_obj")
            
    except ValueError:
        raise ValueError(err_msg)
    except BaseException:
        raise TypeError(err_msg)

    return None



def if_real_numpy_array(obj, obj_name):
    r"""Check whether input object is a real-valued numpy array.

    If the input object is not a real-valued numpy array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a numpy array of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    if not czekitout.isa.real_numpy_array(obj):
        err_msg = _if_real_numpy_array_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_real_numpy_array_1d(obj, obj_name):
    r"""Check whether input object is a real-valued 1D numpy array.

    If the input object is not a real-valued 1D numpy array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a 1D numpy array of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.real_numpy_array_1d(obj):
        err_msg = _if_real_numpy_array_1d_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_real_numpy_matrix(obj, obj_name):
    r"""Check whether input object is a real-valued 2D numpy array.

    If the input object is not a real-valued 2D numpy array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a 2D numpy array of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.real_numpy_matrix(obj):
        err_msg = _if_real_numpy_matrix_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_real_two_column_numpy_matrix(obj, obj_name):
    r"""Check whether input object is a real-valued 2D two-column numpy array.

    If the input object is not a real-valued 2D two-column numpy array, then a
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

    """
    _check_obj_name(obj_name)

    if not czekitout.isa.real_two_column_numpy_matrix(obj):
        err_msg = _if_real_two_column_numpy_matrix_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_real_numpy_array_3d(obj, obj_name):
    r"""Check whether input object is a real-valued 3D numpy array.

    If the input object is not a real-valued 3D numpy array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a 3D numpy array of real numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.real_numpy_array_3d(obj):
        err_msg = _if_real_numpy_array_3d_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_nonnegative_numpy_array(obj, obj_name):
    r"""Check whether input object is a nonnegative numpy array.

    If the input object is not a nonnegative numpy array, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a numpy array of nonnegative numbers.

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

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.nonnegative_numpy_array(obj):
        err_msg = _if_nonnegative_numpy_array_err_msg_1.format(obj_name)
        if czekitout.isa.real_numpy_array(obj):
            raise ValueError(err_msg)
        raise TypeError(err_msg)

    return None



def if_nonnegative_numpy_matrix(obj, obj_name):
    r"""Check whether input object is a nonnegative numpy matrix.

    If the input object is not a nonnegative numpy matrix, then an exception is
    raised with the message::

        The object ``<obj_name>`` must be a numpy matrix of nonnegative numbers.

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

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.nonnegative_numpy_matrix(obj):
        err_msg = _if_nonnegative_numpy_matrix_err_msg_1.format(obj_name)
        if czekitout.isa.real_numpy_matrix(obj):
            raise ValueError(err_msg)
        raise TypeError(err_msg)

    return None



def if_bool(obj, obj_name):
    r"""Check whether input object is boolean.

    If the input object is not boolean, then a `TypeError` exception is raised
    with the message::

        The object ``<obj_name>`` must be boolean.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    try:
        if not isinstance(obj, bool):
            check_if_int = if_int  # Alias for readability.
            check_if_int(obj, obj_name)
            obj_after_rounding = round(complex(obj).real)
            if obj_after_rounding not in (0, 1):
                raise
    except:
        unformatted_err_msg = _if_bool_err_msg_1
        err_msg = unformatted_err_msg.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_bool_matrix(obj, obj_name):
    r"""Check whether input object is a 2D boolean array.

    If the input object is not a 2D boolean array, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be a boolean matrix.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    err_msg = _if_bool_matrix_err_msg_1.format(obj_name)

    try:
        for elem_of_obj in obj:
            for elem_of_elem_of_obj in elem_of_obj:
                check_if_bool = if_bool  # Alias for readability.
                check_if_bool(elem_of_elem_of_obj, "elem_of_elem_of_obj")
    except:
        raise TypeError(err_msg)

    return None



def if_bool_array_3d(obj, obj_name):
    r"""Check whether input object is a 3D boolean array.

    If the input object is not a 3D boolean array, then a `TypeError` exception
    is raised with the message::

        The object ``<obj_name>`` must be a 3D boolean array.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    err_msg = _if_bool_array_3d_err_msg_1.format(obj_name)

    try:
        for elem_of_obj in obj:
            check_if_bool_matrix = if_bool_matrix  # Alias for readability.
            check_if_bool_matrix(elem_of_obj, "elem_of_obj")
    except:
        raise TypeError(err_msg)

    return None



def if_complex_numpy_array(obj, obj_name):
    r"""Check whether input object is a complex-valued numpy array.

    If the input object is not a complex-valued numpy array, then a `TypeError`
    exception is raised with the message::

        The object ``<obj_name>`` must be a numpy array of complex numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    if not czekitout.isa.complex_numpy_array(obj):
        err_msg = _if_complex_numpy_array_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_complex_numpy_matrix(obj, obj_name):
    r"""Check whether input object is a complex-valued 2D numpy array.

    If the input object is not a complex-valued 2D numpy array, then a
    `TypeError` exception is raised with the message::

        The object ``<obj_name>`` must be a 2D numpy array of complex numbers.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)
    
    if not czekitout.isa.complex_numpy_matrix(obj):
        err_msg = _if_complex_numpy_matrix_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



def if_callable(obj, obj_name):
    r"""Check whether input object is callable.

    If the input object is not callable, then a `TypeError` exception is raised
    with the message::

        The object ``<obj_name>`` must be callable.

    where <obj_name> is replaced by the contents of the string ``obj_name``.

    Parameters
    ----------
    obj : any type
        Input object.
    obj_name : `str`
        Name of the input object.

    """
    _check_obj_name(obj_name)

    if not callable(obj):
        err_msg = _if_callable_err_msg_1.format(obj_name)
        raise TypeError(err_msg)

    return None



###########################
## Define error messages ##
###########################

_check_obj_name_err_msg_1 = \
    ("The object ``{}`` must be an instance of the class `{}`.")

_check_accepted_types_err_msg_1 = \
    ("The object ``{}`` must be a non-empty sequence of instances of the class "
     "`{}`.")

_if_instance_of_any_accepted_types_err_msg_1 = \
    _check_obj_name_err_msg_1
_if_instance_of_any_accepted_types_err_msg_2 = \
    ("The object ``{}`` must be an instance of one of the following classes: "
     "{}.")

_if_dict_like_err_msg_1 = \
    ("The object ``{}`` must be dictionary-like.")

_if_str_like_err_msg_1 = \
    ("The object ``{}`` must be string-like.")

_if_str_like_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence, where each element is string-like.")

_if_one_of_any_accepted_strings_err_msg_1 = \
    ("The object ``accepted_strings`` must be a non-empty sequence, where "
     "each element is string-like.")
_if_one_of_any_accepted_strings_err_msg_2 = \
    ("The object ``{}`` must be set to ``'{}'``.")
_if_one_of_any_accepted_strings_err_msg_3 = \
    ("The object ``{}`` must be set to one of the following strings: ``{}``.")

_if_scalar_err_msg_1 = \
    ("The object ``{}`` must be a scalar.")

_if_float_err_msg_1 = \
    ("The object ``{}`` must be a real number.")

_if_float_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of real numbers.")

_if_positive_float_err_msg_1 = \
    ("The object ``{}`` must be a positive real number.")

_if_positive_float_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of positive real numbers.")

_if_nonnegative_float_err_msg_1 = \
    ("The object ``{}`` must be a nonnegative real number.")

_if_nonnegative_float_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of nonnegative real numbers.")

_if_int_err_msg_1 = \
    ("The object ``{}`` must be an integer.")

_if_int_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of integers.")

_if_positive_int_err_msg_1 = \
    ("The object ``{}`` must be a positive integer.")

_if_positive_int_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of positive integers.")

_if_nonnegative_int_err_msg_1 = \
    ("The object ``{}`` must be a nonnegative integer.")

_if_nonnegative_int_seq_err_msg_1 = \
    ("The object ``{}`` must be a sequence of nonnegative integers.")

_if_single_dim_slice_like_err_msg_1 = \
    ("The object ``{}`` must be an integer, a sequence of integers, or a "
     "`slice` object.")

_if_multi_dim_slice_like_err_msg_1 = \
    ("The object ``{}`` must be a sequence of items which contains at most one "
     "item being a sequence of integers, and the remaining items being `slice` "
     "objects and/or integers.")

_if_pair_of_floats_err_msg_1 = \
    ("The object ``{}`` must be a pair of real numbers.")

_if_pair_of_positive_floats_err_msg_1 = \
    ("The object ``{}`` must be a pair of positive real numbers.")

_if_pair_of_nonnegative_floats_err_msg_1 = \
    ("The object ``{}`` must be a pair of nonnegative real numbers.")

_if_pair_of_ints_err_msg_1 = \
    ("The object ``{}`` must be a pair of integers.")

_if_pair_of_positive_ints_err_msg_1 = \
    ("The object ``{}`` must be a pair of positive integers.")

_if_pair_of_nonnegative_ints_err_msg_1 = \
    ("The object ``{}`` must be a pair of nonnegative integers.")

_if_quadruplet_of_nonnegative_ints_err_msg_1 = \
    ("The object ``{}`` must be a quadruplet of nonnegative integers.")

_if_pairs_of_floats_err_msg_1 = \
    ("The object ``{}`` must be a sequence of pairs of real numbers.")

_if_pairs_of_ints_err_msg_1 = \
    ("The object ``{}`` must be a sequence of pairs of integers.")

_if_pairs_of_nonnegative_ints_err_msg_1 = \
    ("The object ``{}`` must be a sequence of pairs of nonnegative integers.")

_if_real_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a numpy array of real numbers.")

_if_real_numpy_array_1d_err_msg_1 = \
    ("The object ``{}`` must be a 1D numpy array of real numbers.")

_if_real_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a 2D numpy array of real numbers.")

_if_real_two_column_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a two-column numpy matrix of real numbers.")

_if_real_numpy_array_3d_err_msg_1 = \
    ("The object ``{}`` must be a 3D numpy array of real numbers.")

_if_nonnegative_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a numpy array of nonnegative numbers.")

_if_nonnegative_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a numpy matrix of nonnegative numbers.")

_if_bool_err_msg_1 = \
    ("The object ``{}`` must be boolean.")

_if_bool_matrix_err_msg_1 = \
    ("The object ``{}`` must be a boolean matrix.")

_if_bool_array_3d_err_msg_1 = \
    ("The object ``{}`` must be a 3D boolean array.")

_if_complex_numpy_array_err_msg_1 = \
    ("The object ``{}`` must be a numpy array of complex numbers.")

_if_complex_numpy_matrix_err_msg_1 = \
    ("The object ``{}`` must be a 2D numpy array of complex numbers.")

_if_callable_err_msg_1 = \
    ("The object ``{}`` must be callable.")
