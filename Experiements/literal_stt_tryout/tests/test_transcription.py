from types import SimpleNamespace

from transcription import OpenAITranscriber


def test_openai_transcriber_requests_literal_transcription_in_selected_language(tmp_path):
    audio_path = tmp_path / "turn-1.webm"
    audio_path.write_bytes(b"recorded speech")

    class RecordingTranscriptions:
        def create(self, **request):
            self.request = request
            return SimpleNamespace(text="um I I goed there")

    transcriptions = RecordingTranscriptions()
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=transcriptions))

    transcript = OpenAITranscriber(client=client)(audio_path, "en-US")

    assert transcript == "um I I goed there"
    assert transcriptions.request["model"] == "gpt-transcribe"
    assert transcriptions.request["languages"] == ["en"]
    assert transcriptions.request["response_format"] == "json"
    assert "fillers" in transcriptions.request["prompt"]
    assert "Do not correct grammar" in transcriptions.request["prompt"]
    assert transcriptions.request["file"].closed


def test_openai_transcriber_uses_portuguese_instructions_for_portuguese_audio(tmp_path):
    audio_path = tmp_path / "turn-1.webm"
    audio_path.write_bytes(b"fala gravada")

    class RecordingTranscriptions:
        def create(self, **request):
            self.request = request
            return SimpleNamespace(text="eu eu foi ontem")

    transcriptions = RecordingTranscriptions()
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=transcriptions))

    OpenAITranscriber(client=client)(audio_path, "pt-BR")

    assert transcriptions.request["languages"] == ["pt"]
    assert "Preserve hesitações" in transcriptions.request["prompt"]
    assert "Não corrija a gramática" in transcriptions.request["prompt"]
