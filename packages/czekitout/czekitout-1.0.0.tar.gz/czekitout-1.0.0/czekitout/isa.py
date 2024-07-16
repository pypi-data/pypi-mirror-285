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
r"""Contains functions that facilitate type-checking.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For general array handling.
import numpy as np



##################################
## Define classes and functions ##
##################################

# List of public objects in objects.
__all__ = ["numpy_array",
           "scalar_numpy_array",
           "real_numpy_array",
           "nonnegative_numpy_array",
           "complex_numpy_array",
           "bool_numpy_array",
           "numpy_array_1d",
           "numpy_matrix",
           "two_column_numpy_matrix",
           "real_numpy_array_1d",
           "real_numpy_matrix",
           "nonnegative_numpy_matrix",
           "complex_numpy_matrix",
           "numpy_array_3d",
           "real_numpy_array_3d",
           "real_two_column_numpy_matrix",
           "bool_numpy_matrix",
           "bool_numpy_array_3d"]



def numpy_array(obj):
    r"""Returns ``True`` if input object is a numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a numpy array, otherwise it
        is set to ``False``.

    """
    result = isinstance(obj, np.ndarray)

    return result



def scalar_numpy_array(obj):
    r"""Returns ``True`` if input object is a numpy array of scalars.

    We define a scalar as a number that is boolean, an integer, real-valued, or
    complex-valued.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a numpy array of scalars, 
        otherwise it is set to ``False``.

    """
    is_numpy_array = numpy_array  # Alias for readability.
    
    if is_numpy_array(obj):
        try:
            obj.astype(complex)
            result = not np.any(np.isnan(obj))
        except:
            result = False
    else:
        result = False

    return result



def real_numpy_array(obj):
    r"""Returns ``True`` if input object is a real-valued numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a real-valued numpy array, 
        otherwise it is set to ``False``.

    """
    is_scalar_numpy_array = scalar_numpy_array  # Alias for readability.
    
    if is_scalar_numpy_array(obj):
        result = np.isrealobj(obj)
    else:
        result = False

    return result



def nonnegative_numpy_array(obj):
    r"""Returns ``True`` if input object is a nonnegative numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a nonnegative numpy array, 
        otherwise it is set to ``False``.

    """
    is_real_numpy_array = real_numpy_array  # Alias for readability.
    
    if is_real_numpy_array(obj):
        result = bool(np.all(obj >= 0))
    else:
        result = False

    return result



def complex_numpy_array(obj):
    r"""Returns ``True`` if input object is a complex-valued numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a complex-valued numpy 
        array, otherwise it is set to ``False``.

    """
    is_scalar_numpy_array = scalar_numpy_array  # Alias for readability.
    
    if is_scalar_numpy_array(obj):
        result = bool(np.iscomplexobj(obj))
    else:
        result = False

    return result



def bool_numpy_array(obj):
    r"""Returns ``True`` if input object is a boolean numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a boolean numpy array,
        otherwise it is set to ``False``.

    """
    is_scalar_numpy_array = scalar_numpy_array  # Alias for readability.
    
    if is_scalar_numpy_array(obj):
        result = (obj.dtype == bool)
    else:
        result = False

    return result



def numpy_array_1d(obj):
    r"""Returns ``True`` if input object is a 1D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a 1D numpy array, otherwise 
        it is set to ``False``.

    """
    is_numpy_array = numpy_array  # Alias for readability.

    if is_numpy_array(obj):
        result = (len(obj.shape) == 1)
    else:
        result = False

    return result



def numpy_matrix(obj):
    r"""Returns ``True`` if input object is a 2D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a 2D numpy array, otherwise 
        it is set to ``False``.

    """
    is_numpy_array = numpy_array  # Alias for readability.

    if is_numpy_array(obj):
        result = (len(obj.shape) == 2)
    else:
        result = False

    return result



def two_column_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a 2D two-column numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a 2D two-column numpy array,
        otherwise it is set to ``False``.

    """
    is_numpy_matrix = numpy_matrix  # Alias for readability.

    if is_numpy_matrix(obj):
        result = (obj.shape[1] == 2)
    else:
        result = False

    return result



def real_numpy_array_1d(obj):
    r"""Returns ``True`` if input object is a real-valued 1D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a real-valued 1D numpy 
        array, otherwise it is set to ``False``.

    """
    is_numpy_array_1d = numpy_array_1d  # Alias for readability.
    is_real_numpy_array = real_numpy_array  # Alias for readability.

    result = (is_numpy_array_1d(obj) and is_real_numpy_array(obj))

    return result



def real_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a real-valued 2D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a real-valued 2D numpy 
        array, otherwise it is set to ``False``.

    """
    is_numpy_matrix = numpy_matrix  # Alias for readability.
    is_real_numpy_array = real_numpy_array  # Alias for readability.

    result = (is_numpy_matrix(obj) and is_real_numpy_array(obj))

    return result



def nonnegative_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a nonnegative 2D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a nonnegative 2D numpy 
        array, otherwise it is set to ``False``.

    """
    is_numpy_matrix = \
        numpy_matrix  # Alias for readability.
    is_nonnegative_numpy_array = \
        nonnegative_numpy_array  # Alias for readability.

    result = (is_numpy_matrix(obj) and is_nonnegative_numpy_array(obj))

    return result



def complex_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a complex-valued 2D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a complex-valued 2D numpy 
        array, otherwise it is set to ``False``.

    """
    is_numpy_matrix = numpy_matrix  # Alias for readability.
    is_complex_numpy_array = complex_numpy_array  # Alias for readability.

    result = (is_numpy_matrix(obj) and is_complex_numpy_array(obj))

    return result



def numpy_array_3d(obj):
    r"""Returns ``True`` if input object is a 3D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a 3D numpy array, otherwise 
        it is set to ``False``.

    """
    is_numpy_array = numpy_array  # Alias for readability.

    if is_numpy_array(obj):
        result = (len(obj.shape) == 3)
    else:
        result = False

    return result



def real_numpy_array_3d(obj):
    r"""Returns ``True`` if input object is a real-valued 3D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a real-valued 3D numpy 
        array, otherwise it is set to ``False``.

    """
    is_numpy_array_3d = numpy_array_3d  # Alias for readability.
    is_real_numpy_array = real_numpy_array  # Alias for readability.

    result = (is_numpy_array_3d(obj) and is_real_numpy_array(obj))

    return result



def real_two_column_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a real-valued 2D two-column numpy 
    array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a real-valued 2D two-column 
        numpy array, otherwise it is set to ``False``.

    """
    # Aliases for readability.
    is_two_column_numpy_matrix = two_column_numpy_matrix
    is_real_numpy_array = real_numpy_array

    result = (is_two_column_numpy_matrix(obj) and is_real_numpy_array(obj))

    return result



def bool_numpy_matrix(obj):
    r"""Returns ``True`` if input object is a boolean 2D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a bolean 2D numpy array, 
        otherwise it is set to ``False``.

    """
    is_numpy_matrix = numpy_matrix  # Alias for readability.
    is_bool_numpy_array = bool_numpy_array  # Alias for readability.

    result = (is_numpy_matrix(obj) and is_bool_numpy_array(obj))

    return result



def bool_numpy_array_3d(obj):
    r"""Returns ``True`` if input object is a boolean 3D numpy array.

    Parameters
    ----------
    obj : any type
        Input object.

    Returns
    -------
    result : `bool`
        ``result`` is set to ``True`` if ``obj`` is a boolean 3D numpy array, 
        otherwise it is set to ``False``.

    """
    is_numpy_array_3d = numpy_array_3d  # Alias for readability.
    is_bool_numpy_array = bool_numpy_array  # Alias for readability.

    result = (is_numpy_array_3d(obj) and is_bool_numpy_array(obj))

    return result



###########################
## Define error messages ##
###########################
