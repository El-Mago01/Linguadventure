# Request Summary: Literal Speech-to-Text Experiment

## Goal

Build a self-contained experiment for LinguAdventure that determines how literally spoken language can be transcribed before the transcript is sent to an LLM for grammatical correction.

The central requirement is to preserve what the learner actually said, including:

- Grammar mistakes.
- Fillers and hesitations.
- Repeated words.
- False starts and self-corrections.
- Incomplete phrases.
- Names, numbers, and code-switching.

The speech-to-text system must not silently improve, correct, or reinterpret the learner's language.

## Experiment

The frontend records one utterance and processes it through two independent paths:

1. Browser-native `SpeechRecognition` produces a frontend transcript.
2. `MediaRecorder` captures the original audio and uploads it to a Flask backend, where OpenAI `gpt-transcribe` produces a second transcript.

The backend preserves the browser transcript exactly as received and stores it separately from the OpenAI result. A SHA-256 checksum verifies that transport did not change the browser transcript.

The original audio is retained as the source of truth because no probabilistic speech-to-text system can guarantee a perfectly literal transcript.

## Evaluation Workflow

For each conversation turn, the tester can:

- Select Portuguese (Portugal), Portuguese (Brazil), or English (United States).
- Record and replay the original utterance.
- Compare the browser and backend transcripts side by side.
- Enter a manual reference based on the recording.
- Review word error rate and counts of missing, added, and changed words.
- Delete all recordings and metadata for the current session explicitly.

## Technical Boundaries

- All implementation and generated experiment data remain under `Experiements/literal_stt_tryout/`.
- The experiment is local-only and is not published.
- OpenAI credentials are read from an experiment-local, untracked `.env` file.
- Recordings and transcript metadata remain on disk until the user deletes the session.
- No grammatical-correction LLM is included yet; this experiment evaluates only the literal speech-to-text stage.

## Intended Production Direction

Backend speech-to-text is the recommended primary production path because it provides control over the transcription provider, prompt, raw audio, auditing, and repeatable evaluation. Browser speech recognition remains useful as a fast baseline and fallback comparison, but its internal normalization behavior is not fully controllable.
