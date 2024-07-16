# pylint: disable=missing-function-docstring

import sys

import pytest

from _appmap.importer import Importer, wrap_exec_module
from _appmap.wrapt.wrappers import BoundFunctionWrapper


def test_exec_module_protection(monkeypatch):
    """
    Test that recording.wrap_exec_module properly protects against
    rewrapping a wrapped exec_module function.  Repeatedly wrap
    the function, up to the recursion limit, then call the wrapped
    function.  If wrapping protection is working properly, there
    won't be a problem.  If wrapping protection is broken, this
    test will fail with a RecursionError.
    """

    def exec_module():
        pass

    def do_import(*args, **kwargs):  # pylint: disable=unused-argument
        pass

    monkeypatch.setattr(Importer, "do_import", do_import)
    f = exec_module
    for _ in range(sys.getrecursionlimit()):
        f = wrap_exec_module(f)

    f()
    assert True


@pytest.mark.appmap_enabled(config="appmap-exclude-fn.yml")
@pytest.mark.usefixtures("with_data_dir")
def test_excluded(verify_example_appmap):
    def check_imports(*_):
        #  pylint: disable=import-outside-toplevel, import-error
        from example_class import ExampleClass  # pyright: ignore[reportMissingImports]

        #  pylint: enable=import-outside-toplevel, import-error

        assert isinstance(ExampleClass.instance_method, BoundFunctionWrapper)
        assert not isinstance(ExampleClass.another_method, BoundFunctionWrapper)

    verify_example_appmap(check_imports, "instance_method")
