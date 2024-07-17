# (c) 2024 Michał Górny
# SPDX-License-Identifier: GPL-2.0-or-later

"""pytest plugin to check whether Python modules can be imported"""

import pytest

from pytest_import_check.importer import import_path, SUFFIXES


__version__ = "0.0.2"


def pytest_addoption(parser):
    group = parser.getgroup("import-check", "import checks")
    group.addoption("--import-check",
                    action="store_true",
                    help="Check whether all Python modules that can be found "
                         "are importable")


def pytest_configure(config):
    config.addinivalue_line("markers", "importcheck: Import checking tests")


def pytest_collect_file(file_path, parent):
    if not parent.config.option.import_check:
        return None
    if not file_path.name.endswith(SUFFIXES):
        return None
    return ImportCheckFile.from_parent(parent=parent, path=file_path)


class ImportCheckFile(pytest.File):
    def collect(self):
        return [ImportCheckItem.from_parent(self, name="import-check")]


class ImportCheckItem(pytest.Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_marker("importcheck")

    def runtest(self):
        import_path(self.fspath,
                    mode=self.config.getoption("--import-mode"),
                    root=self.config.rootpath,
                    consider_namespace_packages=
                        self.config.getini("consider_namespace_packages"))

    def repr_failure(self, exc_info):
        if exc_info.errisinstance(SyntaxError):
            return exc_info.exconly()
        else:
            exc_info.traceback = exc_info.traceback.cut(self.fspath)
        return super().repr_failure(exc_info)

    def reportinfo(self):
        return (
            self.fspath,
            None,
            self.config.invocation_dir.bestrelpath(self.fspath),
        )
