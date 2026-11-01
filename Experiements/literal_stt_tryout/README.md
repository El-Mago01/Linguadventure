# Literal STT Lab

A local LinguAdventure experiment that records one utterance and compares:

1. Browser `SpeechRecognition` output.
2. OpenAI `gpt-transcribe` output generated from the saved audio.
3. A manual reference entered after replaying the recording.

The backend stores the browser transcript without trimming, capitalization, punctuation, or grammar changes. The original recording remains the source of truth because no speech-to-text system can guarantee a perfectly literal result.

## Run locally

From this directory:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
.venv/bin/python app.py
```

Open <http://127.0.0.1:5050>. Browsers permit microphone access on localhost. Chrome desktop or Android provides the most useful browser-recognition comparison; unsupported browsers can still record audio for backend transcription.

Recordings and JSON metadata are stored below `recordings/<session-uuid>/` and remain there until **Delete this session** is used. Both `.env` and `recordings/` are git-ignored.

## Run tests

```bash
.venv/bin/pytest -q
node tests/metrics.test.mjs
```

The Python tests cover exact Unicode/whitespace preservation, successful and failed provider calls, validation, persistence, upload limits, and scoped deletion. The JavaScript tests cover transcript normalization, WER/error classification, and the transport checksum.

## What to evaluate

Try fillers, repetitions, false starts, ungrammatical phrases, names, numbers, code-switching, and background noise. For each saved turn, replay the audio and type a manual reference. The UI reports WER plus missing, added, and changed word counts for each engine.
