import pytest

from clipp import utils


class TestDescriptor:

    def test_assingment_and_access(self, obj_with_descriptor):
        """
        Confirm that attribute assignment and attribute access work as
        expected.
        """
        obj = obj_with_descriptor(utils.Descriptor)
        obj.attr = 10
        assert "attr" in obj.__dict__
        assert obj.attr == 10

    def test_attribute_deletion(self, obj_with_descriptor):
        """
        Confirm that attribute deletion works as expected.
        """
        obj = obj_with_descriptor(utils.Descriptor)
        obj.attr = 10
        del obj.attr
        assert "attr" not in obj.__dict__


class TestDataDescriptor:

    def test_assingment_and_access(self, obj_with_descriptor):
        """
        Confirm that attribute assignment and attribute access work as
        expected.
        """
        obj = obj_with_descriptor(utils.DataDescriptor)
        obj.attr = 10
        assert "attr" in obj.__dict__
        assert obj.attr == 10

    def test_attribute_deletion(self, obj_with_descriptor):
        """
        Confirm that attribute deletion works as expected.
        """
        obj = obj_with_descriptor(utils.DataDescriptor)
        obj.attr = 10
        del obj.attr
        assert "attr" not in obj.__dict__


def test_index_view():
    """
    Confirm that we receive the expected value when indexing a view or
    view-like object.
    """
    max_num = 100
    table = dict.fromkeys(range(max_num), "x")
    # Confirm that every number in range [-max_num, max_num) returns the
    # expected value. These numbers should produce valid indicies for slicing.
    for i in range(-max_num, max_num):
        assert utils.index_view(table.values(), i) == "x"

    too_big = max_num + 1
    too_small = -1 * max_num - 1
    # Confirm that an index number which is out of range produces a value
    # error if it is too small, and a stop iteration error if it is too large.
    for num, err in ((too_small, ValueError), (too_big, StopIteration)):
        with pytest.raises(err):
            utils.index_view(table.keys(), num)


class TestPolymap:

    def test_update(self, polymap):
        # Perform an initial check for a key we know to exist in the mapping.
        assert polymap["a"] == 1
        # Perform an update on the value we just checked as well as an update
        # which binds an unbound key.
        polymap.update({"a": 0, ("e", "g"): 5}, x=10)
        # Ensure that membership testing works as expected in light of the
        # update.
        assert ("a", "b") in polymap
        assert ("e", "g")
        assert "c" in polymap

        # Check that the keymap has maintained its data integrity.
        for group in (("a", "b"), ("e", "g")):
            for char in group:
                assert polymap._keymap[char] == group

        assert polymap._keymap["e"] == ("e", "g")

        # Check that keys were assigned their expected values.
        for group in (("a", 0), ("g", 5), ("c", 2)):
            key, value = group
            assert polymap[key] == value

    @pytest.mark.parametrize("key", (["a", ("c", "d")]))
    def test___delitem__(self, key, polymap):
        # Test first for the membership of a key we know to exist.
        assert key in polymap
        # Delete the key we just checked.
        del polymap[key]
        # Enusre that the key has been deleted.
        assert key not in polymap


class TestSetFamily:

    def test__coerce(self, family):
        coerced = family._coerce(["a", "b", "c"])
        assert isinstance(coerced, frozenset)

    def test_superset(self, family):
        """
        Confirm that the superset property returns all of the values from
        each of the groups as a single set.
        """
        assert family.superset == frozenset(["a", "b", "c", "d", "e"])

    def test_includes(self, family):
        """
        Confirm that calling `includes` without the superset argument
        produces a `frozenset` containing only the members which contain the
        supplied value. Likewise, confirm that supplying a value which is
        not contained in any of the members produces an empty `frozenset`.
        """
        expected = frozenset([
            frozenset({"a", "b"}),
            frozenset({"b", "c"}),
        ])
        assert family.includes("b") == expected
        assert family.includes("z") == utils.SetFamily([])

        # Same as above test, but with superset set to `True`.
        expected = frozenset(["a", "b", "c"])
        assert family.includes("b", superset=True) == expected
        assert family.includes("z", superset=True) == frozenset([])

    def test___contains__(self, family):
        """Basic membership testing."""
        family.update({
            frozenset({"a", "b"}),
            frozenset({"c", "d"}),
            frozenset({"a", "e"})
        })
        assert ("a" in family) is True
        assert ("z" in family) is False

    def test_update(self, family):
        """
        Confirm that updating the ordinal set with multiple sets produces
        the expected result--a `SetFamily` object containing all members from
        all supplied sets, as well as all incumbent members of the set.
        """
        family.update([("a", "e"), ("x", "y")], [("x", "z")])
        expected = utils.SetFamily([
            frozenset({"a", "b"}),
            frozenset({"b", "c"}),
            frozenset({"d", "e"}),
            frozenset({"a", "e"}),
            frozenset({"x", "y"}),
            frozenset({"x", "z"})
        ])
        assert family == expected
