.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.tool.tinject -- Automate creation of sources
.. :Created:   Wed 13 Apr 2016 11:22:34 CEST
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016, 2017, 2018, 2022, 2024 Lele Gaifax
..

===========================
 metapensiero.tool.tinject
===========================

Automate creation of sources
============================

:author: Lele Gaifax
:contact: lele@metapensiero.it
:license: GNU General Public License version 3 or later

This is a simple tool that takes a YAML_ declarative configuration of `actions`, each
describing the set of `steps` needed to accomplish it, and realizes one or more actions
possibly interpolating a set of dynamic values inserted by the user.

I've written it with the goal of taking away, as much as possible, the tediousness of creating
new content in a PatchDB_ setup.

There is a myriad of similar tools around, but most of them are either targeted at
bootstrapping a hierarchy of files and directories (that is, a *one-shot* operation, for
example to create the *skeleton* of a new Python package, like cookiecutter_ to mention one) or
belong to a very specific domain (an example of this category may be ZopeSkel_).

To fulfill my goal I needed a tool able to perform an arbitrary list of operations, primarily:

* create a directory
* create a file with a particular content
* change the content of an existing file

It obviously needs to be *parametric* in almost every part: the pathnames and the actual
content of the files must be determined by a *template* interpolated with a set of *values*.

This is what Jinja2_ excels at.

Since the values are mostly *volatile* (that is, almost all of them change from one invocation
to the other), I first used the excellent `inquirer`_ library to prompt the user, but at some
point I was asked about compatibility with Windows and thus I switched to `whaaaaat`_, that
being based on `prompt_toolkit`_ was more promising on that. More recently, due to a long
inactivity on the port to version 2 of prompt_toolkit (see `whaaaaat's issue 23`_), I replaced
it with `questionary`_: thankfully they all expose a very similar interface, so that was very
easily achieved (hint: the latter two effectively inherit from the former).

.. contents::

.. _cookiecutter: https://pypi.python.org/pypi/cookiecutter
.. _inquirer: https://pypi.org/project/inquirer/
.. _jinja2: http://jinja.pocoo.org/
.. _patchdb: https://pypi.python.org/pypi/metapensiero.sphinx.patchdb
.. _prompt_toolkit: https://pypi.org/project/prompt_toolkit/
.. _questionary: https://pypi.org/project/questionary/
.. _whaaaaat's issue 23: https://github.com/finklabs/whaaaaat/issues/23
.. _whaaaaat: https://pypi.python.org/pypi/whaaaaat
.. _yaml: http://yaml.org/
.. _zopeskel: https://pypi.python.org/pypi/ZopeSkel


Configuration
-------------

The YAML configuration file may be composed by one or two *documents*: an optional *global
section* and a mandatory one containing the list of available `actions`, each of them being
basically a list of `steps`.


Global section
~~~~~~~~~~~~~~

The first *document* contains a set of optional global settings, in particular:

* the options to instantiate the Jinja2 *environment*
* a set of file *headers*, one for each kind of file
* a list of *steps* to be performed at every invocation


Jinja2 environment
++++++++++++++++++

To avoid clashes with the syntax used by Python's ``format()`` minilanguage, the `default
environment settings`__ are the following:

block_start_string
  The start of a block is ``<<``, instead of the default ``{%``

block_end_string
  The end of a block is ``>>``, instead of the default ``%}``

variable_start_string
  A variable is introduced by ``«``, instead of the classic ``{{``

variable_end_string
  A variable ends with ``»``, and not with the classic ``}}``

extensions
  The extension ``jinja2_time.TimeExtension`` is automatically selected

keep_trailing_newline
  By default the trailing newline is *not* discarded

Obviously any Jinja2 template defined by the configuration must adhere to these settings. If
you don't like them, or if you want define different ones, you can put an entry like the
following in the globals section of the configuration::

  jinja:
    block_start_string: "[["
    block_end_string: "]]"
    variable_start_string: "<<"
    variable_end_string: ">>"

__ http://jinja.pocoo.org/docs/dev/api/#jinja2.Environment


File headers
++++++++++++

This is a map between a file *suffix* and a template that will be automatically injected in the
render's context as the variable ``header``. For example, should you need to generate a Pascal
unit, you could insert the following::

  headers:
    pas: |
      (*« "*" * 70 »
       * Project: «package_name»
       * Created: «timestamp»
       *« "*" * 70 »)


Initial steps
+++++++++++++

This is a list of steps to be executed unconditionally at startup. In particular it may be used
to gather some values from arbitrary places to initialize the *answers*, to prompt the user for
a common set of values and to define custom *steps*. As an example, you could say::

  steps:
    - python:
        script: |
          import os, pwd, sys

          class InitCustomAnswersWithoutPrompt(Step):
              def __init__(self, state, config):
                  super().__init__(state, config)
                  self.name = config['name']
                  self.value = config['value']

              def announce(self):
                  self.state.announce('*', "Inject %s=%s", self.name, self.value)

              def __call__(self, *args, **kwargs):
                  return {self.name: self.value, python_version: sys.version}

          register_step('initcustom', InitCustomAnswersWithoutPrompt)

          myself = pwd.getpwuid(os.getuid())
          state.answers['author_username'] = myself.pw_name
          state.answers['author_fullname'] = myself.pw_gecos.split(',')[0]

    ## Here you can execute the new kind of operation defined above

    - initcustom:
        name: "myextravar"
        value: "thevalue"


Actions
~~~~~~~

An *action* is identified by a unique name and carries an optional description, an optional set
of prompts specific to the action and a list of one or more steps.

The following is a complete example::

  create_top_level_setup_py:
    description: Create top level setup.py

    prompt:
      - package_name:
          message: The name of the Python package

    steps:
      - createdir:
          directory: src

      - createfile:
          directory: src
          filename: setup.py
          content: |
            # Hi, I'm the setup.py file for «package_name»


Steps
~~~~~

A *step* is some kind of *operation* that must be carried out. The name of the step identifies
the kind of operation, and its value is used to specify the needed parameters. So, in the
example above, we have two steps, ``createdir`` and ``createfile``, each requiring its specific
arguments map.

A step may be conditionally skipped specifying an expression in its ``when`` setting: if
present, the operation will be performed only when the expression evaluates to true.

This is the list of available operation kinds:

changefile
  Perform some quite simple changes to the content of an existing file.

  Required configuration:

    directory
      The directory containing the file to be changed

    filename
      The name of the existing file within the given directory

    changes
      A list of tweaks: there are currently just three types, one that *add* some content
      *before* a given *marker*, one to add the content *after* it and one that *insert* some
      content *between* a marker *and* another marker keeping the block sorted

  Example::

    - changefile:
        directory: src
        filename: listofitems.txt
        changes:
          - add: "«newitemname»\n"
            before: "\n;; items delimiter\n"
          - add: "«newitemname»\n"
            after: "\n;; reversed insertion order\n"

    - changefile:
        directory: src
        filename: __init__.py
        changes:
          - insert: "from .«table_name» import «table_name»\n"
            between: "\n## ⌄⌄⌄ tinject import marker ⌄⌄⌄, please don't remove!\n"
            and: "\n## ⌃⌃⌃ tinject import marker ⌃⌃⌃, please don't remove!\n"

createdir
  Create a directory and its parents.

  Required configuration:

    directory
      The directory to be created

  Example::

    - createdir:
        directory: src/my/new/package

createfile
  Create a new file with a particular content.

  Required configuration:

    directory
      The directory contained the file to be created

    filename
      The name of the new file

    content
      A Jinja2 template that will be rendered and written to the new file

  Example::

    - createfile:
        directory: "«docs_dir»/«schema_name»/tables"
        filename: "«table_name».sql"
        description: Structure of table «schema_name».«table_name»
        ## The template may be either inline or included from an external file
        content: !include 'table.sql'

prompt
  Ask the user for some information bits.

  Required configuration: a list of dictionaries, each representing a `questionary's
  question`__.

  Example::

    - prompt:
        - name_of_the_variable:
            message: Tell me the value
            default: "default value"

        - different_kind_of_input:
            message: Select the variant
            kind: list
            choices:
              - Big
              - Medium
              - Small

  __ https://questionary.readthedocs.io/en/stable/pages/advanced.html#question-dictionaries

  The following options are treated in a special way:

  filter
    an expression that will be wrapped inside a ``lambda`` function accepting a single argument
    named `value`: the user input will be passed to the function, and its result will be the
    actual answer to the question

  regexp
    a `regular expression`__ that should match the entire input, otherwise it will be rejected

    __ https://docs.python.org/3/library/re.html#regular-expression-syntax

    .. hint:: Entering the correct `regular expression` may be a bit tricky, because it must
              obey ``YAML`` syntax, that has its own `escaped characters`__ within
              `double-quoted scalars`__: enter them with using `single-quoted syntax`__
              instead.

              __ https://yaml.org/spec/1.2.2/#57-escaped-characters
              __ https://yaml.org/spec/1.2.2/#double-quoted-style
              __ https://yaml.org/spec/1.2.2/#732-single-quoted-style

  regexp_error
    the error message emitted when ``regexp`` does not match the user's input; it may contain a
    single ``%s`` placeholder, that will be replaced by the regexp itself; by default
    ``"Invalid input, does not match required regexp “%s”"``

  validate
    an expression that will be wrapped inside a ``lambda`` function accepting a single argument
    named `value`: the user input will be passed to the function, that must be return a boolean
    to indicate whether the value is acceptable or not

  validate_error
    the error message emitted when the ``validate`` expression yields ``False``; by default
    ``"Invalid input"``

  when
    a `Jinja2 expression`__ that will be evaluated with the answers of previous questions: if
    it yields ``False``, then the question will be skipped

    __ https://jinja.palletsprojects.com/en/3.1.x/templates/#expressions

  Full example::

    - prompt:
        - disclose_age:
            kind: confirm
            message: Do you agree to disclose your age?
        - age_in_years:
            message: Your age in moons
            regexp: '\d+'
            regexp_error: Only digits are allowed
            validate: '4*13 < int(value) < 120*13'
            validate_error: Oh come on, be serious!
            # Convert back in whole years
            filter: "round(int(value) / 13)"
            when: "disclose_age is true"

python
  Execute an arbitrary Python script.

  Required configuration:

    script
      The code of the script

  The script is executed with a context containing the class ``Step``, the function
  ``register_step`` and the global ``state`` of the program.

  See the `initial steps`_ above for an example.

repeat
  Repeat a list of substeps.

  Required configuration:

    steps
      The list of substeps to repeat

  Optional configuration:

    description
      A message string, emitted at the start, if given

    answers
      The name of variable holding a list of answers, when one substep is a ``prompt``

    count
      The number of iterations

    when
      A Jinja boolean expression: if given it's evaluated once before the loop begins, that
      gets executed only when it expression's value is true, otherwise no repetition happens at
      all; the expression may refer to previous answers, even those collected while looping
      (that is, the variable specified by the ``answers`` option)

    until
      A Jinja boolean expression: if given (and ``count`` is **not**), then the loop is
      terminated when the condition is false

    again_message
      When neither ``count`` nor ``until`` are specified, the step will explicitly ask
      confirmation about looping again, at the end of all substeps execution

  See ``examples/repeat.yml`` for an example.


Sample session
--------------

Create a new schema with a new table::

  $ tinject --verbose apply examples/patchdb.yml new_schema new_table

  * Execute Python script
  [?] Author fullname (author_fullname): Lele Gaifax
  [?] Author username (author_username): lele
  [?] Author email (author_email): «author_username»@example.com
  [?] Fully qualified package name (package_name): package.qualified.name
  [?] Timestamp (timestamp): << now 'local', '%a %d %b %Y %H:%M:%S %Z' >>
  [?] Year (year): << now 'local', '%Y' >>
  [?] Distribution license (license): GNU General Public License version 3 or later
  [?] Copyright holder (copyright): © «year» «author_fullname»
  [?] Root directory of Sphinx documentation (docs_dir): docs/database
  [?] Root directory of SQLAlchemy model sources (model_dir): src/«package_name|replace(".","/")»

  =====================
   Create a new schema
  =====================
  [?] Name of the new schema (schema_name): public

  * Create directory docs/database/public

  * Create file docs/database/public/index.rst

  * Create directory docs/database/public/tables

  * Create file docs/database/public/tables/index.rst

  * Create directory src/package/qualified/name/entities/public

  * Create file src/package/qualified/name/entities/public/__init__.py

  * Create directory src/package/qualified/name/tables/public

  * Create file src/package/qualified/name/tables/public/__init__.py

  ====================
   Create a new table
  ====================
  [?] Schema name of the new table (schema_name): public
  [?] Name of the new table (table_name): things
  [?] Description of the new table (table_description): The table ``«schema_name».«table_name»`` contains...
  [?] Name of the corresponding entity (entity_name): Thing

  * Create file docs/database/public/tables/things.rst

  * Create file docs/database/public/tables/things.sql

  * Create file src/package/qualified/name/entities/public/thing.py

  * Change file src/package/qualified/name/entities/public/__init__.py

    - insert “from .thing import T…” between “## ⌄⌄⌄ tinject impo…” and “## ⌃⌃⌃ tinject impo…”

    - add “mapper(Thing, t.thi…” after “## ⌃⌃⌃ tinject impo…”

  * Create file src/package/qualified/name/tables/public/things.py

  * Change file src/package/qualified/name/tables/public/__init__.py

    - insert “from .things import …” between “## ⌄⌄⌄ tinject impo…” and “## ⌃⌃⌃ tinject impo…”

Verify::

  $ cat src/package/qualified/name/entities/public/__init__.py
  # -*- coding: utf-8 -*-
  # :Project:   package.qualified.name -- Entities in schema public
  # :Created:   mer 15 giu 2016 13:24:54 CEST
  # :Author:    Lele Gaifax <lele@example.com>
  # :License:   GNU General Public License version 3 or later
  # :Copyright: © 2016 Lele Gaifax
  #

  from sqlalchemy.orm import mapper

  from ...tables import public as t

  ## ⌄⌄⌄ tinject import marker ⌄⌄⌄, please don't remove!
  from .thing import Thing

  ## ⌃⌃⌃ tinject import marker ⌃⌃⌃, please don't remove!

  mapper(Thing, t.things, properties={
  })

Add another table::

  $ tinject --verbose apply examples/patchdb.yml new_table

  * Execute Python script
  [?] Author fullname (author_fullname): Lele Gaifax
  [?] Author username (author_username): lele
  [?] Author email (author_email): «author_username»@example.com
  [?] Fully qualified package name (package_name): package.qualified.name
  [?] Timestamp (timestamp): << now 'local', '%a %d %b %Y %H:%M:%S %Z' >>
  [?] Year (year): << now 'local', '%Y' >>
  [?] Distribution license (license): GNU General Public License version 3 or later
  [?] Copyright holder (copyright): © «year» «author_fullname»
  [?] Root directory of Sphinx documentation (docs_dir): docs/database
  [?] Root directory of SQLAlchemy model sources (model_dir): src/«package_name|replace(".","/")»

  ====================
   Create a new table
  ====================
  [?] Schema name of the new table (schema_name): public
  [?] Name of the new table (table_name): thangs
  [?] Description of the new table (table_description): The table ``«schema_name».«table_name»`` contains...
  [?] Name of the corresponding entity (entity_name): Thang

  * Create file docs/database/public/tables/thangs.rst

  * Create file docs/database/public/tables/thangs.sql

  * Create file src/package/qualified/name/entities/public/thang.py

  * Change file src/package/qualified/name/entities/public/__init__.py

    - insert “from .thang import T…” between “## ⌄⌄⌄ tinject impo…” and “## ⌃⌃⌃ tinject impo…”

    - add “mapper(Thang, t.tha…” after “## ⌃⌃⌃ tinject impo…”

  * Create file src/package/qualified/name/tables/public/thangs.py

  * Change file src/package/qualified/name/tables/public/__init__.py

    - insert “from .thangs import …” between “## ⌄⌄⌄ tinject impo…” and “## ⌃⌃⌃ tinject impo…”

Verify::

  $ cat src/package/qualified/name/entities/public/__init__.py
  # -*- coding: utf-8 -*-
  # :Project:   package.qualified.name -- Entities in schema public
  # :Created:   mer 15 giu 2016 13:24:54 CEST
  # :Author:    Lele Gaifax <lele@example.com>
  # :License:   GNU General Public License version 3 or later
  # :Copyright: © 2016 Lele Gaifax
  #

  from sqlalchemy.orm import mapper

  from ...tables import public as t

  ## ⌄⌄⌄ tinject import marker ⌄⌄⌄, please don't remove!
  from .thang import Thang
  from .thing import Thing

  ## ⌃⌃⌃ tinject import marker ⌃⌃⌃, please don't remove!

  mapper(Thang, t.thangs, properties={
  })

  mapper(Thing, t.things, properties={
  })


Batch mode
----------

There are cases when all the *variables* are already known and thus there's no need to
interactively prompt the user to get the job done.

The ``apply`` action accepts the options ``--prompt-only`` and ``--answers-file`` to make that
possible.

The former can be used to collect needed information and print that back, or write them into a
YAML file with ``--output-answers``::

  $ tinject apply -p -o pre-answered.yml patchdb.yml new_schema
  ? Author fullname (author_fullname) Lele Gaifax
  ? Author username (author_username) lele
  ? Author email (author_email) «author_username»@example.com
  ? Fully qualified package name (package_name) package.qualified.name
  ? Timestamp (timestamp) << now 'local', '%a %d %b %Y %H:%M:%S %Z' >>
  ? Year (year) << now 'local', '%Y' >>
  ? Distribution license (license) GNU General Public License version 3 or later
  ? Copyright holder (copyright) © «year» «author_fullname»
  ? Root directory of Sphinx documentation (docs_dir) docs/database
  ? Root directory of SQLAlchemy model sources (model_dir) src/«package_name|replace(".","/")»
  ? Name of the new schema (schema_name) public

If you put those settings into a YAML file, you can then execute the action in batch mode::

  $ tinject -v apply -a pre-answered.yml patchdb.yml new_schema

  * Execute Python script

  =====================
   Create a new schema
  =====================

  * Create directory docs/database/public

  * Create file docs/database/public/index.rst

  * Create directory docs/database/public/tables

  * Create file docs/database/public/tables/index.rst

  * Create directory src/package/qualified/name/entities/public

  * Create file src/package/qualified/name/entities/public/__init__.py

  * Create directory src/package/qualified/name/tables/public

  * Create file src/package/qualified/name/tables/public/__init__.py
