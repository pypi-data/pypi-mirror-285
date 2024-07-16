jugmt: JUst Give Me Tables
==========================

.. image:: https://img.shields.io/badge/docs-GitHub%20Pages-blue
    :target: https://safl.github.io/jugmt/
    :alt: Documentation

.. image:: https://github.com/safl/jugmt/actions/workflows/bd.yaml/badge.svg
    :target: https://github.com/safl/jugmt/actions/workflows/bd.yaml
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/safl/jugmt/badge.svg?branch=main
   :target: https://coveralls.io/github/safl/jugmt?branch=main

.. image:: https://img.shields.io/pypi/v/jugmt
    :target: https://pypi.org/project/jugmt/
    :alt: PyPI

.. image:: https://img.shields.io/github/license/safl/jugmt
    :target: https://opensource.org/licenses/LGPL-2.1
    :alt: License

**jugmt** is a minimalistic **spex** (SPecification EXtractor)
**implementation** with a codebase less than **200** lines of Python::

  ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━┓
  ┃ Language          ┃ Files ┃     % ┃ Code ┃    % ┃ Comment ┃    % ┃
  ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━┩
  │ Python            │     7 │  63.6 │  160 │ 49.8 │      61 │ 19.0 │
  │ JSON              │     1 │   9.1 │   58 │ 52.7 │       0 │  0.0 │
  │ HTML+Django/Jinja │     1 │   9.1 │   46 │ 86.8 │       0 │  0.0 │
  │ __empty__         │     1 │   9.1 │    0 │  0.0 │       0 │  0.0 │
  │ __duplicate__     │     1 │   9.1 │    0 │  0.0 │       0 │  0.0 │
  ├───────────────────┼───────┼───────┼──────┼──────┼─────────┼──────┤
  │ Sum               │    11 │ 100.0 │  264 │ 54.5 │      61 │ 12.6 │
  └───────────────────┴───────┴───────┴──────┴──────┴─────────┴──────┘

The tool extracts figure information and tables from ``.docx`` files, generates
**HTML** and **JSON**, and validates the **JSON** using a **JSON** schema.

It does so for various NVMe specification documents, including Base, Boot, MI,
NVM, ZNS, KV, PCI, RDMA, and TCP. It performs these tasks in about **5 seconds**
on an i7-1360P using a single thread and uses approximately **500MB** of memory.

This implementation is designed to be efficient and lightweight. For more
information on the source code, extracted table formats, and validation, please
refer to the `online documentation <https://safl.dk/jugmt>`_
