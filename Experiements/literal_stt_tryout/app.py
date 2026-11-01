import hashlib
import json
from pathlib import Path
import re
import shutil
from time import perf_counter
from uuid import UUID

from flask import Flask, jsonify, render_template, request

from dotenv import load_dotenv

from transcription import OpenAITranscriber


def create_app(config=None):
    load_dotenv(Path(__file__).parent / ".env")
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,
        RECORDINGS_ROOT=Path(__file__).parent / "recordings",
        TRANSCRIBER=OpenAITranscriber(),
    )
    if config:
        app.config.update(config)

    @app.errorhandler(413)
    def upload_too_large(_error):
        return jsonify(error="Audio upload is too large"), 413

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/turns")
    def create_turn():
        for required_field in (
            "session_id",
            "turn_id",
            "language",
            "browser_transcript",
        ):
            if required_field not in request.form:
                return jsonify(error=f"Missing required field: {required_field}"), 400

        session_id = request.form["session_id"]
        turn_id = request.form["turn_id"]
        language = request.form["language"]
        browser_transcript = request.form["browser_transcript"]

        try:
            valid_session_id = str(UUID(session_id))
        except (ValueError, AttributeError):
            return jsonify(error="Invalid session_id"), 400
        if valid_session_id != session_id.lower():
            return jsonify(error="Invalid session_id"), 400
        if not re.fullmatch(r"turn-[1-9][0-9]*", turn_id):
            return jsonify(error="Invalid turn_id"), 400
        if language not in {"pt-PT", "pt-BR", "en-US"}:
            return jsonify(error="Unsupported language"), 400
        audio = request.files.get("audio")
        audio_extensions = {
            "audio/webm": "webm",
            "audio/ogg": "ogg",
            "audio/mp4": "m4a",
            "audio/wav": "wav",
            "audio/x-wav": "wav",
        }
        if audio is None or audio.mimetype not in audio_extensions:
            return jsonify(error="Unsupported audio type"), 400
        try:
            browser_alternatives = json.loads(
                request.form.get("browser_alternatives", "[]")
            )
            browser_confidence = float(request.form.get("browser_confidence", 0))
            if not isinstance(browser_alternatives, list):
                raise ValueError
            if not 0 <= browser_confidence <= 1:
                raise ValueError
        except (json.JSONDecodeError, TypeError, ValueError):
            return jsonify(error="Invalid browser diagnostics"), 400

        session_directory = Path(app.config["RECORDINGS_ROOT"]) / session_id
        audio_extension = audio_extensions[audio.mimetype]
        audio_path = session_directory / f"{turn_id}.{audio_extension}"
        metadata_path = session_directory / f"{turn_id}.json"
        possible_evidence = [metadata_path]
        possible_evidence.extend(
            session_directory / f"{turn_id}.{extension}"
            for extension in set(audio_extensions.values())
        )
        if any(path.exists() for path in possible_evidence):
            return jsonify(error="Turn already exists"), 409

        session_directory.mkdir(parents=True, exist_ok=True)
        audio.save(audio_path)

        started_at = perf_counter()
        try:
            provider_transcript = app.config["TRANSCRIBER"](audio_path, language)
            provider = {"status": "ok", "transcript": provider_transcript}
        except Exception as error:
            provider = {"status": "error", "message": str(error)}
        provider["latency_ms"] = round((perf_counter() - started_at) * 1000)

        checksum = hashlib.sha256(browser_transcript.encode("utf-8")).hexdigest()
        metadata = {
            "session_id": session_id,
            "turn_id": turn_id,
            "language": language,
            "browser_transcript": browser_transcript,
            "browser_alternatives": browser_alternatives,
            "browser_confidence": browser_confidence,
            "recorded_at": request.form.get("recorded_at"),
            "browser": {"user_agent": request.user_agent.string},
            "browser_utf8_sha256": checksum,
            "recording": f"{session_id}/{turn_id}.{audio_extension}",
            "provider": provider,
        }
        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=2)

        return jsonify(metadata), 201

    @app.delete("/api/sessions/<session_id>")
    def delete_session(session_id):
        try:
            valid_session_id = str(UUID(session_id))
        except (ValueError, AttributeError):
            return jsonify(error="Invalid session_id"), 400
        if valid_session_id != session_id.lower():
            return jsonify(error="Invalid session_id"), 400

        session_directory = Path(app.config["RECORDINGS_ROOT"]) / session_id
        if not session_directory.is_dir():
            return jsonify(error="Session not found"), 404
        shutil.rmtree(session_directory)
        return jsonify(deleted=session_id)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
