.. -*- coding: utf-8 -*-

Changes
-------

1.7 (2024-07-19)
~~~~~~~~~~~~~~~~

* Fix a newbie glitch in question's `when` expression


1.6 (2024-07-18)
~~~~~~~~~~~~~~~~

* Fix compatibility with older snakes, not using an f-string syntax introduced by Python 3.12


1.5 (2024-07-17)
~~~~~~~~~~~~~~~~

* Exploit ``questionary``'s `filter`, `validate` and `when` options


1.4 (2024-07-10)
~~~~~~~~~~~~~~~~

* Fix compatibility with ruamel.yaml 0.18.x


1.3 (2023-12-07)
~~~~~~~~~~~~~~~~

* Switch build system to pdm-backend__

  __ https://pypi.org/project/pdm-backend/


1.2 (2023-09-07)
~~~~~~~~~~~~~~~~

* **Breaking change**: replace the old ``{file_description}`` interpolation into the file
  header with a *normal* Jinja2 context variable, ``description``


1.1 (2022-07-21)
~~~~~~~~~~~~~~~~

* Switch build system to pdm-pep517__

  __ https://pypi.org/project/pdm-pep517/


1.0 (2022-06-29)
~~~~~~~~~~~~~~~~

* Renew development environment:

  - modernized packaging using `PEP 517`__ and hatchling__
  - replaced virtualenv with nix__

  __ https://peps.python.org/pep-0517/
  __ https://hatch.pypa.io/latest/config/build/#build-system
  __ https://nixos.org/guides/how-nix-works.html


0.8 (2018-12-16)
~~~~~~~~~~~~~~~~

- Use questionary__ instead of whaaaaat_: the latter seems stale, the former is based on
  `prompt_toolkit`_ v2

  __ https://pypi.org/project/questionary/

- Use `ruamel.yaml`__ instead of PyYAML__

  __ https://pypi.org/project/ruamel.yaml/
  __ https://pypi.org/project/PyYAML/

- New option ``--answers-file`` mode, to read answers from a ``YAML`` file


0.7 (2017-06-02)
~~~~~~~~~~~~~~~~

- Use whaaaaat_ instead of inquirer_: being based on `prompt_toolkit`_ it offers a better
  user experience and should be usable also under Windows


0.6 (2017-03-22)
~~~~~~~~~~~~~~~~

- Minor tweak, no externally visible changes


0.5 (2016-11-07)
~~~~~~~~~~~~~~~~

- All steps support a “when” condition


0.4 (2016-06-16)
~~~~~~~~~~~~~~~~

- New changefile tweak to insert a line in a sorted block


0.3 (2016-05-22)
~~~~~~~~~~~~~~~~

- New ability to repeat a list of substeps


0.2 (2016-05-19)
~~~~~~~~~~~~~~~~

- First release on PyPI


0.1 (2016-04-26)
~~~~~~~~~~~~~~~~

- Initial effort
