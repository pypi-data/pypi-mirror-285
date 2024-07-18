# (c) 2024 Michał Górny
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import subprocess
import sys

import pytest


@pytest.fixture(params=[False, True])
def py_limited_api(request):
    yield request.param


@pytest.fixture
def build_c_ext(pytester, py_limited_api):
    def inner(code=""):
        pytester.makefile(".c", test=f"""
            #define PY_SSIZE_T_CLEAN
            #include <Python.h>

            static struct PyModuleDef testmodule = {{
                PyModuleDef_HEAD_INIT,
                .m_name = "test",
                .m_doc = NULL,
                .m_size = -1,
                .m_methods = NULL,
            }};

            extern void this_function_does_not_exist();

            PyMODINIT_FUNC
            PyInit_test(void)
            {{
                {code}
                return PyModule_Create(&testmodule);
            }}
        """)
        pytester.makepyfile(setup=f"""
            from setuptools import setup, Extension

            setup(name="test",
                  version="0",
                  ext_modules=[
                      Extension(name="test",
                                sources=["test.c"],
                                py_limited_api={py_limited_api}),
                  ])
        """)
        subprocess.run([sys.executable, "setup.py", "build_ext", "-i"],
                       check=True)
    yield inner


def test_c_ext(run, build_c_ext):
    build_c_ext()
    result = run("--ignore=setup.py")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["test.*::import-check*PASSED*"])


@pytest.mark.skipif(os.name == "nt",
                    reason="Python on Windows crashes on loading an extension "
                    "with undefined symbols (!)")
def test_c_ext_undefined_symbol(run, build_c_ext):
    build_c_ext(code="this_function_does_not_exist();")
    result = run("--ignore=setup.py")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test.*::import-check*FAILED*",
        "E*ImportError*test.*this_function_does_not_exist*",
    ])
    # check whether we got nicely stripped traceback
    result.stdout.no_fnmatch_line("*/_pytest/*")
    result.stdout.no_fnmatch_line("*importlib*")


def test_c_ext_import_py(pytester, run, build_c_ext):
    pytester.makepyfile(foo="")
    build_c_ext(code='if (!PyImport_ImportModule("foo")) return NULL;')
    result = run("--ignore=setup.py")
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines([
        "foo.py::import-check*PASSED*",
        "test.*::import-check*PASSED*",
    ])


def test_c_ext_import_nonexisting(pytester, run, build_c_ext):
    build_c_ext(code="""
        if (!PyImport_ImportModule("this_package_really_shouldnt_exist"))
            return NULL;
    """)
    result = run("--ignore=setup.py")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test.*::import-check*FAILED*",
        "E*ModuleNotFoundError*this_package_really_shouldnt_exist*",
    ])
    # check whether we got nicely stripped traceback
    result.stdout.no_fnmatch_line("*/_pytest/*")
    result.stdout.no_fnmatch_line("*importlib*")


def test_c_ext_import_syntax_error(pytester, run, build_c_ext):
    pytester.makepyfile(bad="/ / /")
    build_c_ext(code="""
        if (!PyImport_ImportModule("bad"))
            return NULL;
    """)
    result = run("--ignore=setup.py", "--ignore=bad.py")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test.*::import-check*FAILED*",
        "E*File*/bad.py*line 1",
        "*/ / /",
        "*SyntaxError:*",
    ])
    # check whether we got nicely stripped traceback
    result.stdout.no_fnmatch_line("*/_pytest/*")
    result.stdout.no_fnmatch_line("*importlib*")


def test_c_ext_exception(pytester, run, build_c_ext):
    build_c_ext(code="""
        PyErr_SetString(PyExc_ValueError, "Imma failing");
        return NULL;
    """)
    result = run("--ignore=setup.py")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test.*::import-check*FAILED*",
        "E*ValueError*Imma failing*",
    ])
    # check whether we got nicely stripped traceback
    result.stdout.no_fnmatch_line("*/_pytest/*")
    result.stdout.no_fnmatch_line("*importlib*")


def test_c_ext_import_indirect_nonexisting(pytester, run, build_c_ext):
    pytester.makepyfile(bad="import this_package_really_shouldnt_exist")
    build_c_ext(code="""
        if (!PyImport_ImportModule("bad"))
            return NULL;
    """)
    result = run("--ignore=setup.py", "--ignore=bad.py")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "test.*::import-check*FAILED*",
        ">*import this_package_really_shouldnt_exist",
        "E*ModuleNotFoundError:*",
        "bad.py:1: ModuleNotFoundError",
    ])
    # check whether we got nicely stripped traceback
    result.stdout.no_fnmatch_line("*/_pytest/*")
    result.stdout.no_fnmatch_line("*importlib*")
