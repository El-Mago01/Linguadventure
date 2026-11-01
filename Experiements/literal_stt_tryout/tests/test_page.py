from app import create_app


def test_home_page_exposes_the_comparison_workflow(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Literal STT Lab" in page
    assert 'id="language"' in page
    assert 'value="pt-PT"' in page
    assert 'value="pt-BR"' in page
    assert 'value="en-US"' in page
    assert 'id="record-button"' in page
    assert 'id="final-transcript"' in page
    assert 'id="provisional-transcript-row"' in page
    assert 'id="interim-transcript"' in page
    assert "Finalized browser transcript" in page
    assert "Provisional · may change" in page
    assert 'id="turn-results"' in page
    assert "Delete this session" in page
    assert "No transcript is guaranteed to be perfectly literal" in page
