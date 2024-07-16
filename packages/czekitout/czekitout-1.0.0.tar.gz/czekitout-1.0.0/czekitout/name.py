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
r"""Contains a function that determines the fully-qualified class name of a 
given object or class.

"""



#####################################
## Load libraries/packages/modules ##
#####################################



##################################
## Define classes and functions ##
##################################

# List of public objects in objects.
__all__ = ["fully_qualified_class_name"]



def fully_qualified_class_name(obj_or_cls):
    r"""Get fully qualified class name of given input object or class.

    Parameters
    ----------
    obj_or_cls : any type
        Input object or class.

    Returns
    -------
    result : `str`
        The fully qualified class name of ``obj_or_cls``.

    """
    if isinstance(obj_or_cls, type):
        cls = obj_or_cls
    else:
        obj = obj_or_cls
        cls = obj.__class__

    module = cls.__module__

    if module == "builtins":
        result = cls.__qualname__
    else:
        result = module + "." + cls.__qualname__
    
    return result



###########################
## Define error messages ##
###########################
