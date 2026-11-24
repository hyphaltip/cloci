import cloci.lib.output_data as od


def test_annotation_mngr_skips_without_pfam_or_interpro(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise AssertionError("ann_mngr must not run without --pfam/--interpro")

    monkeypatch.setattr(od, "ann_mngr", boom)
    out = od.annotation_mngr(
        {"o1": []}, {"o1": {"faa": "x", "gff3": "y"}}, str(tmp_path) + "/",
        None, None, {}, str(tmp_path) + "/",
    )
    assert out is None
