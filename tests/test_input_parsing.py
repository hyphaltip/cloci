import pytest

from cloci.lib.input_parsing import RootError, root_tree
from mycotools.lib.kontools import FatalError  # noqa: F401  (import contract)


def test_root_error_is_defined():
    assert issubclass(RootError, Exception)


def test_root_tree_rejects_wrong_arguments_without_typeerror():
    from cogent3 import make_tree

    tree = make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);")
    # three-tip outgroup list must raise RootError, not TypeError
    with pytest.raises(RootError):
        root_tree(tree, outgroup=["a", "b", "c"])


def test_root_tree_two_tip_outgroup_roots():
    from cogent3 import make_tree

    tree = make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);")
    rooted = root_tree(tree, outgroup=["a", "b"])
    assert set(rooted.get_tip_names()) == {"a", "b", "c", "d", "e"}


def test_root_tree_midpoint():
    from cogent3 import make_tree

    tree = make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);")
    rooted = root_tree(tree, midpoint=True)
    assert set(rooted.get_tip_names()) == {"a", "b", "c", "d", "e"}
