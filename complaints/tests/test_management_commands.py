from io import StringIO

from django.core.management import call_command


def test_build_faiss_index():
    out = StringIO()
    call_command("build_faiss_index", stdout=out)
    out.seek(0)
    assert "not implemented" in out.read().lower()