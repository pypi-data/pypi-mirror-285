ScreenPy Playwright
===================

[![Build Status](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)
[![Build Status](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![Supported Versions](https://img.shields.io/pypi/pyversions/screenpy_playwright.svg)](https://pypi.org/project/screenpy_playwright)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

```
TITLE CARD:
                               "ScreenPy Playwright"
TITLE DISAPPEARS.
                                                                      FADE IN:
INT. DOCUMENTATION - GLOAMING

Scene settles on an UNKNOWN MAN, feverishly writing with an overly fancy
quill at a writing desk. Several crumpled papers are around him, but there
is a sizeable stack intact, scrawled with text. The writing desk is butted
against a large window, with a beautiful view of the dwindling sunset.
Bookshelves crammed with books flank the window; it is clear the books are
frequently taken down and put back in different spots. AUDIENCE gently opens
a nearby door.

                              AUDIENCE
                              (whispering)
            Oh! Excuse me, i didn't mean to intrude.

The UNKNOWN MAN does not look up, as if he did not hear AUDIENCE. He continues
writing.

                              NARRATOR (V.O.)
            This young man is the Playwright extension for
            ScreenPy. He is relatively new here, but he has
            quite a large reputation backing him.

                              AUDIENCE
            Can he hear me? And wait, he's a real man?

                              NARRATOR (V.O.)
            He is singularly focused. He is real, in a sense.

                              AUDIENCE
            Does he ever, y'know... eat? Sleep?

                              NARRATOR (V.O.)
            No.

                              AUDIENCE
            All right, you've got a strange definition of "real."

AUDIENCE takes one last look at PLAYWRIGHT before leaving, softly closing
the door behind them.

                                                                      FADE OUT
```


Installation
------------
    pip install screenpy_playwright

or

    pip install screenpy[playwright]


Documentation
-------------
Please check out the [Read The Docs documentation](https://screenpy-playwright-docs.readthedocs.io/en/latest/) for the latest information about this module!

You can also read the [ScreenPy Docs](https://screenpy-docs.readthedocs.io/en/latest/) for more information about ScreenPy in general.


Contributing
------------
You want to contribute? Great! Here are the things you should do before submitting your PR:

1. Fork the repo and git clone your fork.
1. `dev` install the project package:
    1. `pip install -e .[dev]`
    1. Optional (poetry users):
        1. `poetry install --extras dev`
1. Run `pre-commit install` once.
1. Run `tox` to perform tests frequently.
1. Create pull-request from your branch.

That's it! :)
