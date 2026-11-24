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


def test_compile_tree_root_none_uses_midpoint(tmp_path):
    """cloci.main passes root=None when --root is absent: must midpoint-root."""
    from cogent3 import make_tree

    from cloci.lib.input_parsing import compile_tree

    path = tmp_path / "t.newick"
    make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);").write(str(path))
    phylo = compile_tree(["a", "b", "c", "d", "e"], str(path), root=None)
    assert set(phylo.get_tip_names()) == {"0", "1", "2", "3", "4"}


def test_compile_tree_outgroup_list_roots(tmp_path):
    from cogent3 import make_tree

    from cloci.lib.input_parsing import compile_tree

    path = tmp_path / "t.newick"
    make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);").write(str(path))
    phylo = compile_tree(["a", "b", "c", "d", "e"], str(path), root=["a", "b"])
    assert len(phylo.get_tip_names()) == 5


def test_compile_tree_empty_root_list_uses_midpoint(tmp_path):
    """cloci.main passes root=[] when --root is absent (documented default: midpoint)."""
    from cogent3 import make_tree

    from cloci.lib.input_parsing import compile_tree

    path = tmp_path / "t.newick"
    make_tree("((a:1,b:1):1,(c:1,d:1):1,e:1);").write(str(path))
    phylo = compile_tree(["a", "b", "c", "d", "e"], str(path), root=[])
    assert set(phylo.get_tip_names()) == {"0", "1", "2", "3", "4"}
