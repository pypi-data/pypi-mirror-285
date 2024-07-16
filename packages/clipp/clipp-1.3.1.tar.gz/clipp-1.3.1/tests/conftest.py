import pytest

from clipp import core
from clipp import utils


@pytest.fixture
def obj_with_descriptor():

    def _wrapper(descriptor_class, *args, **kwargs):

        class MockClass:
            attr = descriptor_class(*args, **kwargs)

        return MockClass()

    return _wrapper


@pytest.fixture
def polymap():
    return utils.Polymap({("a", "b"): 1, ("c", "d"): 2, "e": 3, "z": 0})


@pytest.fixture
def family():
    return utils.SetFamily([
        frozenset({"a", "b"}),
        frozenset({"b", "c"}),
        frozenset({"d", "e"}),
    ])


@pytest.fixture
def option():

    def _option(*aliases: str, **kwargs):
        return core.Option(*aliases, **kwargs)

    return _option


@pytest.fixture
def parameter():

    def _parameter(name: str, **kwargs):
        return core.Parameter(name, **kwargs)

    return _parameter


@pytest.fixture
def option_group():
    return core.OptionGroup()


@pytest.fixture
def option_group_multiple():

    def _option_group_multiple(count: int):
        return [core.OptionGroup() for _ in range(count)]

    return _option_group_multiple


@pytest.fixture
def command():
    return core.Command("command")


@pytest.fixture
def subcommand():
    parent = core.Command()
    return core.Subcommand("subcommand", parent=parent)


@pytest.fixture(scope="function")
def parser():
    command = core.Command("sum", version_info="1.0.0")
    command.add_binary_flag("--verbose", "-v", is_global=True)
    command.add_parameter(
        "integers",
        quota="*",
        dtype=int,
        action=sum,
        dest="sum",
    )
    command.add_option("--round", "-r", dtype=int, default=2, const=2)
    command.add_option("--output-file", "-o")
    command.add_option("--format")
    command.make_mutually_exclusive("-o", "--format")
    command.add_option("--mod", "-m", quota=1, dtype=int)
    command.add_option("--div-by", "-d", quota=1, dtype=int)
    command.make_mutually_exclusive("-d", "-m")
    return core.Parser(command)
