from openai import OpenAI


LITERAL_PROMPTS = {
    "en": (
        "Transcribe exactly what is spoken in the audio's original language. "
        "Preserve fillers, repetitions, false starts, incomplete phrases, and mistakes. "
        "Do not correct grammar, improve wording, or add words that were not spoken."
    ),
    "pt": (
        "Transcreva exatamente o que foi dito no idioma original do áudio. "
        "Preserve hesitações, repetições, falsos começos, frases incompletas e erros. "
        "Não corrija a gramática, não melhore a formulação e não acrescente palavras que não foram ditas."
    ),
}


class OpenAITranscriber:
    def __init__(self, client=None):
        self.client = client

    def __call__(self, audio_path, language):
        client = self.client or OpenAI()
        language_hint = {"pt-PT": "pt", "pt-BR": "pt", "en-US": "en"}[language]

        with audio_path.open("rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=audio_file,
                model="gpt-transcribe",
                languages=[language_hint],
                prompt=LITERAL_PROMPTS[language_hint],
                response_format="json",
            )
        return result.text
