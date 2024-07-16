import pytest

from clipp import core


@pytest.mark.parametrize("text, nchars, expected",
    (["", 0, ""], ["", 1, ""], ["abc", 1, "ab"], ["ab", 2, "ab"]))
def test_truncate(text, nchars, expected):
    assert core.truncate(text, nchars) == expected


@pytest.mark.parametrize("text, expected",
    (["", ""],
     [" ", " "],
     ["\t", "\t"],
     [" abc", " "],
     ["\tabc", "\t"],
     ["\t abc", "\t "],
     [" \tabc", " \t"]))
def test_get_indent(text, expected):
    assert core.get_indent(text) == expected


@pytest.mark.parametrize("text, expected, width",
    (["aaaaaa", "aaaaaa", 6],
     ["aaaaaaa", "aaaaaa\na", 6],
     ["aaaa aaaa", "aaaa\naaaa", 6],
     ["aaaa aaaa \n\tbbbb", "aaaa\naaaa\n\tbb\n\tbb", 6]))
def test_fill_paragraph(text, expected, width):
    """
    Enure that the text get wrapped as expected, that newline characters are
    retained and that line indentation is also retained.
    """
    # This is an absolute nightmare to test. Consider the paramatrized tests
    # to be magic incantations. Don't change them, and don't modify the
    # function being tested unless absolutely necessary.
    text = text.expandtabs(4)
    expected = expected.expandtabs(4)
    assert core.fill_paragraph(text, width=width) == expected


@pytest.mark.parametrize("value, expected_error",
    (["-a", ValueError],
     ["a-", ValueError],
     ["ab cd", ValueError],
     ["name", None]))
def test_positional_name_descriptor(
        value,
        expected_error,
        obj_with_descriptor
        ):
    """
    Ensure that the descriptor assigns the value to the attribute so long as
    the value is a valid positional name. Otherwise, ensure that `ValueError`
    is raised.
    """
    obj = obj_with_descriptor(core.PositionalName)
    if expected_error is not None:
        with pytest.raises(expected_error):
            obj.attr = value
    else:
        obj.attr = value
        assert obj.attr == value


@pytest.mark.parametrize("values, is_flag, expected_error",
    ([["--foo", "-f"], False, None],
     [["--foo", "-f"], True, None],
     [["--foo", "-9"], True, None],
     [["--foo", "-9"], False, ValueError],
     [["--foo", "bar"], False, ValueError],
     [["--foo", "bar"], True, ValueError],
     [["-"], True, None],
     [["-"], False, None]))
def test_aliases_descriptor(
        values,
        is_flag,
        expected_error,
        obj_with_descriptor,
        ):
    """
    Ensure that the descriptor assigns the value(s) to the attribute as long
    as the value(s) are valid aliases. Otherwise, ensure that `ValueError` is
    raised.
    """
    obj = obj_with_descriptor(core.Aliases, is_flag=is_flag)
    if expected_error:
        with pytest.raises(expected_error):
            obj.attr = values
    else:
        obj.attr = values
        # Check that the values actually got assigned to the attribute.
        assert obj.attr == values


@pytest.mark.parametrize("value, minsize, expected_error",
    ([0, 0, None], [0.0, 0.0, None],
     [1, -1, None], [1.0, -1.0, None],
     [-1, 0, ValueError], [-1.0, 1.0, ValueError],
     [0.8, 0.9, ValueError], [-1.0, 0.9, ValueError]))
def test_quota_descriptor(
        value,
        minsize,
        expected_error,
        obj_with_descriptor
        ):
    """
    Ensure that the descriptor assigns the value to the attribute as long as
    it meets the minimum size requirement. Otherwise, ensure that `ValueError`
    is raised.
    """
    obj = obj_with_descriptor(core.Quota, minsize=minsize)
    if expected_error:
        with pytest.raises(expected_error):
            obj.attr = value
    else:
        obj.attr = value
        assert obj.attr == value


@pytest.mark.parametrize("values, expected_error",
    ([["a", "b"], None],
     [["-a", "-b"], ValueError],
     [["a", "-"], ValueError],
     [["a", "-99 bar"], ValueError],
     [["a", "-99.0 bar"], ValueError],
     [["a", "-99"], None],
     [["a", "99.0"], None],
     [["a", "foo bar"], None],
     [["a", " fobar "], ValueError]))
def test_choice_descriptor(values, expected_error, obj_with_descriptor):
    """
    Ensure that the descriptor assigns the value(s) to the attribute when the
    value(s) are valid choices. Otherwise, ensure that `ValueError` is raised.
    """
    obj = obj_with_descriptor(core.Choice)
    if expected_error:
        with pytest.raises(expected_error):
            obj.attr = values
    else:
        obj.attr = values
        assert obj.attr == values


@pytest.mark.skip("not implemented")
def test_reference_descriptor():
    """
    Ensure that the subclass references the correct attribute of the parent.
    """

    class MockClass:

        def __init__(self, attr):
            self.attr = attr

    class MockSubclass(MockClass):
        attr = core.Reference("_parent")

        def __init__(self, parent):
            self._parent = parent

    cls = MockSubclass(MockClass("foo"))
    assert cls.attr == "foo"


class TestOption:

    @pytest.mark.parametrize("value, expected",
        ([0, 0], ["*", float("inf")], ["+", float("inf")]))
    def test__coerce_quota_valid(self, value, expected, option):
        assert option("--foo")._coerce_quota(value) == expected

    @pytest.mark.parametrize("value, expected_error",
        (["a", ValueError], [0.5, TypeError], [float("inf"), TypeError]))
    def test__coerce_quota_invalid(self, value, expected_error, option):
        with pytest.raises(expected_error):
            option("--foo")._coerce_quota(value)

    @pytest.mark.parametrize("quota, expected",
        (["+", False], ["*", True], [1, True], [2, False]))
    def test__supports_defaults(self, quota, expected, option):
        assert option("--foo")._supports_defaults(quota) == expected

    @pytest.mark.parametrize("quota, value, expected",
        (["+", 10, 10],
         ["+", None, None],
         ["*", None, []],
         ["*", 10, 10], [1, 10, 10],
         [1, None, None]))
    def test__get_effective_value(self, quota, value, expected, option):
        """
        Ensure that the correct value is returned for the specified quota.
        If no value supplied is `None`, the return value will be `None`, unless
        the quota is zero-or-more (*). In all other cases, the value returned
        should be the value supplied.
        """
        opt = option("--foo", "-f", quota=quota)
        assert opt._get_effective_value(value) == expected

    @pytest.mark.parametrize("quota, values, expected",
        (["+", [], False],
         ["+", [1], True],
         ["*", [], True],
         ["*", [1], True],
         [1, [], False],
         [1, [1], True]))
    def test__meets_quota(self, quota, values, expected, option):
        """
        Ensure that the return value is `True` if the number of values meets
        the quota. Option's with zero-or-more quotas (*) should always
        receive `True`, regardless of the number of values supplied.
        """
        opt = option("--foo", "-f", quota=quota)
        assert opt._meets_quota(values) == expected

    @pytest.mark.parametrize("quota, values",
        (["+", []],
         [1, []],
         [2, [1]],
         [1, []]))
    def test__validate(self, quota, values,  option):
        """
        Test the case in which the number of values does not meet the quota
        and no `const` or `choices` argument is explicitly provided.
        """
        opt = option("--foo", quota=quota)
        with pytest.raises(SystemExit):
            opt._validate(values)

    def test__validate_with_choices(self, option):
        """Test that an invalid choice raises `SystemExit`."""
        opt = option("--foo", "-f", quota=1, choices=["a", "b"])
        with pytest.raises(SystemExit):
            opt._validate(["c"])


class TestOptionGroup:

    @pytest.mark.parametrize("is_global", ([False], [True]))
    def test__add_option(self, is_global, option, option_group):
        opt = option("--foo", is_global=is_global)
        option_group._add_option(opt)
        assert "--foo" in option_group.options
        if not is_global:
            assert "--foo" in option_group.local_options
            assert "--foo" not in option_group.global_options
        else:
            assert "--foo" in option_group.global_options
            assert "--foo" not in option_group.local_options

    def test__check_options(self, option, option_group):
        """
        Ensure that attempts to add an option which shares an alias with
        another option which has already been added leads to a `KeyError`
        being raised.
        """
        option_group._add_option(option("--foo", "-f"))
        with pytest.raises(KeyError):
            option_group._add_option(option("--bar", "-f"))

    @pytest.mark.parametrize("is_global", ([False], [True]))
    def test__remove(self, is_global, option_group):
        optname = "--foo"
        option_group.add_option(optname, is_global=is_global)
        option_group.remove(optname)
        assert optname not in option_group.local_options
        assert optname not in option_group.global_options
        assert optname not in option_group.options

    @pytest.mark.parametrize("aliases, to_include",
        ([["--foo", "--bar"], ["--foo"]],
         [["--foo", "--bar"], None]))
    def test_include(self, aliases, to_include, option_group_multiple):
        """
        Enure that options from the first group get included in the second.
        """
        group1, group2 = option_group_multiple(2)
        for name in aliases:
            group1.add_option(name)

        group2.include(group1, to_include)
        if to_include:
            for name in to_include:
                assert name in group2.options
        else:
            for name in aliases:
                assert name in group2.options

    @pytest.mark.skip("test needed")
    def test_make_dependent(self):
        ...

    @pytest.mark.skip("test needed")
    def test_make_mutually_exclusive(self):
        ...


class TestCommand:

    def test_add_subcommand(self, command):
        subcmd = command.add_subcommand("subcommand")
        assert isinstance(subcmd, core.Subcommand)
        assert subcmd.name in command.subcommands

    def test_add_parameter(self, command, parameter):
        param1 = parameter("foo", quota="*")
        param2 = parameter("bar", quota="*")
        command._add_parameter(param1)
        assert param1.name in command._params
        with pytest.raises(core.AmbiguityError):
            command._add_parameter(param2)

    def test__check_options(self, option, command):
        """
        Ensure that attempts to add an option which shares an alias with
        another option which has already been added causes `KeyError` to be
        raised.
        """
        opt1 = option("--foo", "-f")
        opt2 = option("--bar", "-f")
        command._add_option(opt1)
        assert opt1.name in command.options
        with pytest.raises(KeyError):
            command._add_option(opt2)

    @pytest.mark.parametrize("is_global", ([True], [False]))
    def test_remove(self, is_global, option, command):
        """
        Ensure that the option gets successfully removed after being added.
        Test both the local and global case.
        """
        opt = option("--foo", is_global=is_global)
        command._add_option(opt)
        command.remove(opt.name)
        assert opt.name not in command.options

    def test_remove_param(self, parameter, command):
        """
        Ensure that the parameter gets successfully removed after being added.
        """
        param = parameter("foo")
        command._add_parameter(param)
        command.remove(param.name)
        assert param.name not in command.parameters

    def test_set_help_flag(self, command):
        flag_name = "--show-help"
        command.set_help_flag(flag_name)
        assert "--help" not in command.options
        assert flag_name in command.options
        assert command._help_flag == flag_name

    def test_set_version_flag(self, command):
        flag_name = "--show-version"
        command.set_version_flag(flag_name)
        assert "--version" not in command.options
        assert flag_name in command.options
        assert command._version_flag == flag_name

    @pytest.mark.skip("integration test needed")
    def test_remove_option_dependent(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test_remove_option_mutex(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test__unbind(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test__check_relational_groups(self, command):
        ...

    @pytest.mark.skip("integration test needed")
    def test__check_required(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test__get_default_namespace(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test__preprocess(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test__postprocess(self):
        ...

    @pytest.mark.skip("integration test needed")
    def test_parse(self):
        ...


class TestSubcommand:

    def test__add_option_global(self, option, subcommand):
        opt = option("--foo", is_global=True)
        with pytest.raises(ValueError):
            subcommand._add_option(opt)

    def test__check_options(self, option, subcommand):
        """
        Ensure that attempts to add an option which shares an alias with
        another option which has already been added leads to a `KeyError`
        being raised.
        """
        opt1 = option("--foo", "-f", is_global=True)
        subcommand._parent._add_option(opt1)
        opt2 = option("--foo", "-f")
        opt3 = option("--bar", "-f")
        # We should be able to override global options.
        subcommand._add_option(opt2)
        assert opt1.name in subcommand.options
        with pytest.raises(KeyError):
            subcommand._add_option(opt3)

    def test_remove_local(self, option, subcommand):
        opt = option("--foo")
        subcommand._add_option(opt)
        subcommand.remove(opt.name)
        assert opt.name not in subcommand.options

    def test_remove_global(self, option, subcommand):
        opt = option("--foo", is_global=True)
        subcommand._parent._add_option(opt)
        with pytest.raises(KeyError):
            subcommand.remove(opt.name)


class TestParser:
    from collections import deque

    @pytest.mark.parametrize("arguments, expected",
        ([deque(["--mod11"]), ("11", "--mod")],
         [deque(["--div-by10"]), ("10", "--div-by")],
         [deque(["--round2"]), ("2", "--round")],
         [deque(["--mod--round"]), ("--round", "--mod")]))
    def test__decompose_long_valid(self, arguments: deque, expected, parser):
        tokens = parser._decompose_long(arguments.popleft())
        assert tokens == expected

    @pytest.mark.parametrize("arguments",
        (deque(["--foo11"]), deque(["--bar10"]), deque(["--baz2"])))
    def test__decompose_long_invalid(self, arguments, parser):
        with pytest.raises(SystemExit):
            parser._decompose_long(arguments.popleft())

    @pytest.mark.parametrize("arguments, expected",
        ([deque(["-m11"]), ["11", "-m"]],
         [deque(["-d10"]), ["10", "-d"]],
         [deque(["-r2"]), ["2", "-r"]],
         [deque(["-vr2"]), ["2", "-r", "-v"]],
         [deque(["-rv"]), ["v", "-r"]]))
    def test__decompose_short_valid(self, arguments, expected, parser):
        tokens = parser._decompose_short(arguments.popleft())
        assert tokens == expected

    @pytest.mark.parametrize("arguments",
        (deque(["-f11"]), deque(["-b10"]), deque(["-z2"])))
    def test__decompose_short_invalid(self, arguments, parser):
        with pytest.raises(SystemExit):
            parser._decompose_short(arguments.popleft())

    @pytest.mark.skip("integration test needed")
    def test_parse(self):
        ...
