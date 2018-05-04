.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

===
IDE
===

While PyCharm as an excellent IDE, some aspects of it require licensing, and
the PyDev Plugin for Eclipse (packaged as LiClipse) is fully open source
(although donations are welcome). Therefore this section focuses on using
LiClipse for StorPerf development.


Download
============

.. code-block:: bash

    http://www.liclipse.com/download.html


Storperf virtualenv Interpretor
=================================

Setting up interpreter under PyDev (LiClipse):

* Go to Project -> Properties, PyDev Interpreter:

.. image:: ../images/PyDev_Interpreter.jpeg

* Click to configure an interpreter not listed.

.. image:: ../images/PyDev_Interpreters_List.jpeg

* Click New, and create a new interpreter called StorPerf that points to your
  Virtual Env.

.. image:: ../images/PyDev_New_Interpreter.jpeg

* You should get a pop up similar to:

.. image:: ../images/PyDev_Interpreter_Folders.jpeg

* And then you can change the Interpreter to StorPerf.

.. image:: ../images/PyDev_StorPerf_Interpreter.jpeg


Code Formatting
===============

Pep8 and Flake8 rule. These are part of the Gerrit checks and I'm going to
start enforcing style guidelines soon.

* Go to Window -> Preferences, under PyDev, Editor, Code Style, Code Formatter
  and select autopep8.py for code formatting.

.. image:: ../images/Code_formatter.jpeg

* Next, under Save Actions, enable "Auto-format editor contents before saving",
  and "Sort imports on save".

.. image:: ../images/Save_Actions.jpeg

* And under Imports, select Delete unused imports.

.. image:: ../images/Unused_imports.jpeg

* Go to PyDev -> Editor -> Code Analysis and under the pycodestye.py (pep8),
  select Pep8 as Error.  This flag highlight badly formatted lines as errors.
  These must be fixed before Jenkins will +1 any review.

.. image:: ../images/Code_analysis.jpeg


Import Storperf as Git Project
==============================

I prefer to do the git clone from the command line, and then import that as a
local project in LiClipse.

* From the menu: File -> Import Project

.. image:: ../images/Import_Project.png

|

.. image:: ../images/Local_Repo.png

|

.. image:: ../images/Add_git.png

|

* Browse to the directory where you cloned StorPerf

.. image:: ../images/Browse.png

|

* You should now have storperf as a valid local git repo:

.. image:: ../images/Git_Selection.png

|

* Choose Import as general project

