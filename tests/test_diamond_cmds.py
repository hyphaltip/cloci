import os

import cloci.lib.evo_conco as evo


def _dirs(tmp_path):
    hg, hgx, db = tmp_path / "hg", tmp_path / "hgx", tmp_path / "db"
    for d in (hg, hgx, db):
        d.mkdir()
    return str(hg) + "/", str(hgx) + "/", str(db) + "/"


def _prep(tmp_path, **kw):
    hg_dir, hgx_dir, db_dir = _dirs(tmp_path)
    cmds1, cmds2 = evo.prep_blast_cmds(
        None, {1, 2}, hg_dir, hgx_dir, hg2gene={1: ["a", "b"], 2: ["c", "d", "e"]},
        db_dir=db_dir if kw.pop("use_db_dir", False) else None, **kw,
    )
    return hg_dir, hgx_dir, db_dir, cmds1, cmds2


def _arg(cmd, flag):
    return cmd[list(cmd).index(flag) + 1]


def test_default_threads_is_one_and_databases_stay_in_hgx_dir(tmp_path):
    hg_dir, hgx_dir, db_dir, cmds1, cmds2 = _prep(tmp_path)
    for c in cmds1:
        assert _arg(c, "--threads") == "1"
        assert _arg(c, "--db").startswith(hgx_dir)
    for blastp, mv in cmds2:
        assert _arg(blastp, "--threads") == "1"
        assert _arg(blastp, "--db").startswith(hgx_dir)


def test_threads_parameter_is_used(tmp_path):
    *_, cmds1, cmds2 = _prep(tmp_path, threads=4)
    assert all(_arg(c, "--threads") == "4" for c in cmds1)
    assert all(_arg(b, "--threads") == "4" for b, _ in cmds2)


def test_db_dir_moves_databases_but_not_results(tmp_path):
    hg_dir, hgx_dir, db_dir, cmds1, cmds2 = _prep(tmp_path, use_db_dir=True)
    assert all(_arg(c, "--db").startswith(db_dir) for c in cmds1)
    for blastp, mv in cmds2:
        assert _arg(blastp, "--db").startswith(db_dir)
        # results stay on shared storage and are renamed within one directory (atomic)
        assert _arg(blastp, "-o").startswith(hgx_dir) and _arg(blastp, "-o").endswith(".out.tmp")
        assert mv[1].startswith(hgx_dir) and mv[2].startswith(hgx_dir)


def test_max_target_seqs_is_the_hg_size(tmp_path):
    *_, cmds2 = _prep(tmp_path)
    sizes = sorted(int(_arg(b, "--max-target-seqs")) for b, _ in cmds2)
    assert sizes == [2, 3]


def _capture(monkeypatch):
    seen = {}

    def fake(*a, **k):
        seen.update(k)
        seen["scratch_existed"] = os.path.isdir(k["db_dir"]) if k["db_dir"] else None

    monkeypatch.setattr(evo, "_run_blast", fake)
    return seen


def test_run_blast_uses_and_removes_scratch(monkeypatch, tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("SCRATCH", str(scratch))
    seen = _capture(monkeypatch)
    evo.run_blast({1}, None, "h/", "x/", hg2gene={1: ["a"]})
    assert seen["db_dir"].startswith(str(scratch)) and seen["scratch_existed"]
    assert list(scratch.iterdir()) == []  # temp databases removed
    assert seen["diamond_threads"] == 1


def test_run_blast_without_scratch_or_when_printing_uses_hgx_dir(monkeypatch, tmp_path):
    seen = _capture(monkeypatch)
    monkeypatch.delenv("SCRATCH", raising=False)
    evo.run_blast({1}, None, "h/", "x/", hg2gene={1: ["a"]})
    assert seen["db_dir"] == "x/"
    monkeypatch.setenv("SCRATCH", str(tmp_path))
    evo.run_blast({1}, None, "h/", "x/", printexit=True, hg2gene={1: ["a"]})
    assert seen["db_dir"] == "x/"  # makedb.sh / srch.sh must not point at a temp dir
    evo.run_blast({1}, None, "h/", "x/", skipalgn=True, hg2gene={1: ["a"]})
    assert seen["db_dir"] == "x/"


def test_scratch_removed_even_if_the_run_fails(monkeypatch, tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("SCRATCH", str(scratch))

    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(evo, "_run_blast", boom)
    try:
        evo.run_blast({1}, None, "h/", "x/", hg2gene={1: ["a"]})
    except RuntimeError:
        pass
    assert list(scratch.iterdir()) == []
