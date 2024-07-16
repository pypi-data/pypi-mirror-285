.. _installation_instructions_sec:

Installation instructions
=========================

Installing czekitout
--------------------

For all installation scenarios, first open up the appropriate command line
interface. On Unix-based systems, you would open a terminal. On Windows systems
you would open an Anaconda Prompt as an administrator.

Installing czekitout using pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install ``czekitout`` using ``pip`` is to run the following
command::

  pip install czekitout

The above command will install the latest stable version of ``czekitout``.

To install the latest development version from the main branch of the `czekitout
GitHub repository <https://github.com/mrfitzpa/czekitout>`_, one must first
clone the repository by running the following command::

  git clone https://github.com/mrfitzpa/czekitout.git

Next, change into the root of the cloned repository, and then run the following
command::

  pip install .

Note that you must include the period as well. The above command executes a
standard installation of ``czekitout``.

Optionally, for additional features in ``czekitout``, one can install additional
dependencies upon installing ``czekitout``. To install a subset of additional
dependencies (along with the standard installation), run the following command
from the root of the repository::

  pip install .[<selector>]

where ``<selector>`` can be one of the following:

* ``tests``: to install the dependencies necessary for running unit tests;
* ``examples``: to install the dependencies necessary for running the jupyter
  notebooks stored in ``<root>/examples``, where ``<root>`` is the root of the
  repository;
* ``docs``: to install the dependencies necessary for documentation generation;
* ``all``: to install all of the above optional dependencies.

Installing czekitout using conda
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install ``czekitout`` using the ``conda`` package manager, run the following
command::

  conda install -c conda-forge czekitout

The above command will install the latest stable version of ``czekitout``.

Uninstalling czekitout
----------------------

If ``czekitout`` was installed using ``pip``, then to uninstall, run the
following command from the root of the repository::

  pip uninstall czekitout

If ``czekitout`` was installed using ``conda``, then to uninstall, run the
following command from the root of the repository::

  conda remove czekitout
