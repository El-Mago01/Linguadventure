import io
import json

from app import create_app


def test_browser_transcript_round_trips_and_persists_exactly_when_provider_fails(tmp_path):
    transcript = "  eu, eu fui no café ontem... não hoje 😅  "

    def unavailable_transcriber(_audio_path, _language):
        raise RuntimeError("provider unavailable")

    app = create_app(
        {
            "TESTING": True,
            "RECORDINGS_ROOT": tmp_path,
            "TRANSCRIBER": unavailable_transcriber,
        }
    )

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "76d0d6a1-10a5-4cd5-9de0-82c11c25cf6b",
            "turn_id": "turn-1",
            "language": "pt-PT",
            "browser_transcript": transcript,
            "browser_alternatives": "[]",
            "browser_confidence": "0.72",
            "recorded_at": "2026-10-29T12:00:00.000Z",
            "audio": (io.BytesIO(b"webm-audio"), "turn-1.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["browser_transcript"] == transcript
    assert payload["browser_utf8_sha256"] == (
        "eba89f619d701952ad6947150b3a45e040869e855ffce9a65cbaf33592a74c1c"
    )
    assert payload["provider"]["status"] == "error"

    metadata_path = (
        tmp_path
        / "76d0d6a1-10a5-4cd5-9de0-82c11c25cf6b"
        / "turn-1.json"
    )
    with metadata_path.open(encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
    assert metadata["browser_transcript"] == transcript
    assert (metadata_path.parent / "turn-1.webm").read_bytes() == b"webm-audio"


def test_successful_turn_returns_provider_result_and_browser_diagnostics(tmp_path):
    def transcribe(_audio_path, _language):
        return "eu eu fui no café ontem não hoje"

    app = create_app(
        {
            "TESTING": True,
            "RECORDINGS_ROOT": tmp_path,
            "TRANSCRIBER": transcribe,
        }
    )

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "38790aed-0876-48d9-987c-09fa91218485",
            "turn_id": "turn-2",
            "language": "pt-BR",
            "browser_transcript": "eu fui no café ontem",
            "browser_alternatives": json.dumps(
                [
                    {"transcript": "eu fui no café ontem", "confidence": 0.91},
                    {"transcript": "eu fui no café ontem?", "confidence": 0.72},
                ]
            ),
            "browser_confidence": "0.91",
            "recorded_at": "2026-10-29T12:01:00.000Z",
            "audio": (io.BytesIO(b"more-webm-audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
        headers={"User-Agent": "Literal-STT-Test/1.0"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["provider"]["status"] == "ok"
    assert payload["provider"]["transcript"] == "eu eu fui no café ontem não hoje"
    assert isinstance(payload["provider"]["latency_ms"], int)
    assert payload["browser_alternatives"][1]["confidence"] == 0.72
    assert payload["browser_confidence"] == 0.91
    assert payload["recorded_at"] == "2026-10-29T12:01:00.000Z"
    assert payload["browser"]["user_agent"] == "Literal-STT-Test/1.0"
    assert payload["recording"] == "38790aed-0876-48d9-987c-09fa91218485/turn-2.webm"


def test_turn_rejects_path_traversal_identifiers_without_writing_files(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "../escape",
            "turn_id": "../../turn",
            "language": "en-US",
            "browser_transcript": "hello",
            "audio": (io.BytesIO(b"audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid session_id"}
    assert list(tmp_path.iterdir()) == []


def test_turn_rejects_unsupported_language_before_persisting(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "d419f35a-c5ed-4a1a-a54f-b7e8b439e48d",
            "turn_id": "turn-1",
            "language": "de-DE",
            "browser_transcript": "hallo",
            "audio": (io.BytesIO(b"audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Unsupported language"}
    assert list(tmp_path.iterdir()) == []


def test_turn_rejects_non_audio_upload_before_persisting(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "324ace89-94ea-4f82-838e-42bd96734465",
            "turn_id": "turn-1",
            "language": "en-US",
            "browser_transcript": "hello",
            "audio": (io.BytesIO(b"not audio"), "speech.txt", "text/plain"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Unsupported audio type"}
    assert list(tmp_path.iterdir()) == []


def test_turn_rejects_oversized_request_with_json_error(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "RECORDINGS_ROOT": tmp_path,
            "MAX_CONTENT_LENGTH": 200,
        }
    )

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "e44421b1-a689-4ef8-900e-6d22b41ed702",
            "turn_id": "turn-1",
            "language": "en-US",
            "browser_transcript": "hello",
            "audio": (io.BytesIO(b"a" * 500), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert response.get_json() == {"error": "Audio upload is too large"}
    assert list(tmp_path.iterdir()) == []


def test_delete_session_removes_only_the_selected_session(tmp_path):
    selected_id = "9d3ae3a7-b54e-411b-83d8-35faa8f5be54"
    neighbor_id = "89981521-0f39-4090-bf67-a3dc6dd26f00"
    selected = tmp_path / selected_id
    neighbor = tmp_path / neighbor_id
    selected.mkdir()
    neighbor.mkdir()
    (selected / "turn-1.webm").write_bytes(b"selected")
    (neighbor / "turn-1.webm").write_bytes(b"neighbor")

    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})
    response = app.test_client().delete(f"/api/sessions/{selected_id}")

    assert response.status_code == 200
    assert response.get_json() == {"deleted": selected_id}
    assert not selected.exists()
    assert (neighbor / "turn-1.webm").read_bytes() == b"neighbor"


def test_turn_rejects_malformed_browser_diagnostics_before_persisting(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": "9d3ae3a7-b54e-411b-83d8-35faa8f5be54",
            "turn_id": "turn-1",
            "language": "pt-PT",
            "browser_transcript": "olá",
            "browser_alternatives": "not-json",
            "browser_confidence": "twice as sure",
            "audio": (io.BytesIO(b"audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid browser diagnostics"}
    assert list(tmp_path.iterdir()) == []


def test_turn_reports_a_missing_required_field_as_json(tmp_path):
    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})

    response = app.test_client().post(
        "/api/turns",
        data={
            "turn_id": "turn-1",
            "language": "en-US",
            "browser_transcript": "hello",
            "audio": (io.BytesIO(b"audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required field: session_id"}
    assert list(tmp_path.iterdir()) == []


def test_turn_refuses_to_overwrite_existing_evidence(tmp_path):
    session_id = "b1915db2-0870-4fd2-b586-c50720bd98a1"
    session_directory = tmp_path / session_id
    session_directory.mkdir()
    audio_path = session_directory / "turn-1.webm"
    metadata_path = session_directory / "turn-1.json"
    audio_path.write_bytes(b"original audio")
    metadata_path.write_text('{"browser_transcript":"original"}', encoding="utf-8")

    app = create_app({"TESTING": True, "RECORDINGS_ROOT": tmp_path})
    response = app.test_client().post(
        "/api/turns",
        data={
            "session_id": session_id,
            "turn_id": "turn-1",
            "language": "en-US",
            "browser_transcript": "replacement",
            "audio": (io.BytesIO(b"replacement audio"), "speech.webm", "audio/webm"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "Turn already exists"}
    assert audio_path.read_bytes() == b"original audio"
    assert metadata_path.read_text(encoding="utf-8") == (
        '{"browser_transcript":"original"}'
    )
