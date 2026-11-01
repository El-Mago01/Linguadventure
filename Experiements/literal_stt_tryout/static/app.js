import { utf8Sha256, wordErrorStats } from './metrics.mjs';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const elements = {
    supportBadge: document.querySelector('#support-badge'),
    language: document.querySelector('#language'),
    recordButton: document.querySelector('#record-button'),
    recordLabel: document.querySelector('#record-label'),
    recordHelp: document.querySelector('#record-help'),
    recordTimer: document.querySelector('#record-timer'),
    finalTranscript: document.querySelector('#final-transcript'),
    provisionalTranscriptRow: document.querySelector('#provisional-transcript-row'),
    interimTranscript: document.querySelector('#interim-transcript'),
    captureActions: document.querySelector('#capture-actions'),
    submitTurn: document.querySelector('#submit-turn'),
    discardTurn: document.querySelector('#discard-turn'),
    statusMessage: document.querySelector('#status-message'),
    resultsSection: document.querySelector('#results-section'),
    turnResults: document.querySelector('#turn-results'),
    resultTemplate: document.querySelector('#result-template'),
    sessionShortId: document.querySelector('#session-short-id'),
    turnCount: document.querySelector('#turn-count'),
    deleteSession: document.querySelector('#delete-session'),
    characterPrompt: document.querySelector('#character-prompt'),
};

const prompts = [
    '“Olá! Você voltou. O que aconteceu com a sua mochila?”',
    '“Onde você viu a mochila pela última vez?”',
    '“Você lembra quem estava perto da sua mesa?”',
    '“Como era a mochila? Tinha alguma coisa especial nela?”',
];

const restoredSessionId = sessionStorage.getItem('literal-stt-session');
let sessionId = restoredSessionId || crypto.randomUUID();
let turnNumber = restoredSessionId
    ? Number.parseInt(sessionStorage.getItem('literal-stt-next-turn') || '1', 10)
    : 1;
if (!Number.isInteger(turnNumber) || turnNumber < 1) turnNumber = 1;
let mediaStream = null;
let mediaRecorder = null;
let recognition = null;
let isRecording = false;
let recordedAt = null;
let recordedLanguage = null;
let recordedBlob = null;
let timerStartedAt = 0;
let timerInterval = null;
let browserTranscript = '';
let browserAlternatives = [];
let browserConfidence = 0;
let recognitionError = null;
const audioObjectUrls = [];

sessionStorage.setItem('literal-stt-session', sessionId);
sessionStorage.setItem('literal-stt-next-turn', String(turnNumber));
elements.sessionShortId.textContent = sessionId.slice(0, 8);
if (turnNumber > 1) {
    elements.turnCount.textContent = `${turnNumber - 1} saved ${turnNumber === 2 ? 'turn' : 'turns'}`;
}

function updateSupportBadge() {
    const canRecord = Boolean(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
    if (!canRecord) {
        elements.supportBadge.textContent = 'Audio recording unavailable';
        elements.supportBadge.classList.add('text-red-200');
        elements.recordButton.disabled = true;
        return;
    }
    if (!SpeechRecognition) {
        elements.supportBadge.textContent = 'Backend STT only · browser STT unsupported';
        elements.supportBadge.classList.add('text-amber-200');
        return;
    }
    elements.supportBadge.textContent = 'Browser + backend STT ready';
    elements.supportBadge.classList.add('text-teal-200');
}

function showStatus(message, kind = 'info') {
    const styles = {
        info: ['border', 'border-indigo-300/20', 'bg-indigo-300/10', 'text-indigo-100'],
        success: ['border', 'border-teal-300/20', 'bg-teal-300/10', 'text-teal-100'],
        error: ['border', 'border-red-300/20', 'bg-red-300/10', 'text-red-100'],
    };
    elements.statusMessage.className = 'mt-4 rounded-xl p-4 text-sm';
    elements.statusMessage.classList.add(...styles[kind]);
    elements.statusMessage.textContent = message;
    elements.statusMessage.classList.remove('hidden');
}

function hideStatus() {
    elements.statusMessage.classList.add('hidden');
}

function chooseRecorderOptions() {
    const candidates = [
        'audio/webm;codecs=opus',
        'audio/ogg;codecs=opus',
        'audio/mp4',
    ];
    const supported = candidates.find((type) => MediaRecorder.isTypeSupported(type));
    return supported ? { mimeType: supported } : {};
}

function fileExtension(mimeType) {
    if (mimeType.includes('ogg')) return 'ogg';
    if (mimeType.includes('mp4')) return 'm4a';
    if (mimeType.includes('wav')) return 'wav';
    return 'webm';
}

function joinRecognitionSegments(existing, next) {
    if (!existing) return next;
    if (!next) return existing;
    if (/\s$/.test(existing) || /^\s/.test(next)) return `${existing}${next}`;
    return `${existing} ${next}`;
}

function resetCapture() {
    recordedBlob = null;
    browserTranscript = '';
    browserAlternatives = [];
    browserConfidence = 0;
    recognitionError = null;
    elements.finalTranscript.textContent = 'Waiting for speech…';
    elements.interimTranscript.textContent = 'Listening…';
    elements.provisionalTranscriptRow.classList.add('hidden');
    elements.captureActions.classList.add('hidden');
    elements.captureActions.classList.remove('flex');
    elements.recordButton.disabled = false;
    elements.language.disabled = false;
    hideStatus();
}

function updateTimer() {
    const elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
    const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
    const seconds = String(elapsedSeconds % 60).padStart(2, '0');
    elements.recordTimer.textContent = `${minutes}:${seconds}`;
}

function startBrowserRecognition() {
    if (!SpeechRecognition) return;

    elements.interimTranscript.textContent = 'Listening…';
    recognition = new SpeechRecognition();
    recognition.lang = recordedLanguage;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 5;
    const transcriptBeforeRecognition = browserTranscript;
    const finalSegments = [];
    let restartAfterEnd = true;

    recognition.onresult = (event) => {
        const interimSegments = [];
        for (let index = event.resultIndex; index < event.results.length; index += 1) {
            const result = event.results[index];
            const top = result[0];
            if (result.isFinal) {
                finalSegments[index] = top.transcript;
                browserConfidence = Number.isFinite(top.confidence) ? top.confidence : 0;
                for (let alternativeIndex = 0; alternativeIndex < result.length; alternativeIndex += 1) {
                    browserAlternatives.push({
                        result_index: index,
                        transcript: result[alternativeIndex].transcript,
                        confidence: Number.isFinite(result[alternativeIndex].confidence)
                            ? result[alternativeIndex].confidence
                            : 0,
                    });
                }
            } else {
                interimSegments.push(top.transcript);
            }
        }
        const currentFinalTranscript = finalSegments
            .filter((segment) => segment !== undefined)
            .join('');
        browserTranscript = joinRecognitionSegments(transcriptBeforeRecognition, currentFinalTranscript);
        elements.finalTranscript.textContent = browserTranscript || 'Waiting for finalized speech…';
        elements.interimTranscript.textContent = interimSegments.join('') || 'Listening…';
    };

    recognition.onerror = (event) => {
        if (!['aborted', 'no-speech'].includes(event.error)) restartAfterEnd = false;
        if (event.error !== 'aborted') {
            recognitionError = event.error;
            elements.interimTranscript.textContent = `Browser recognition: ${event.error}. Audio is still being recorded.`;
        }
    };

    recognition.onend = () => {
        if (isRecording && restartAfterEnd) startBrowserRecognition();
    };

    try {
        recognition.start();
    } catch (error) {
        recognitionError = error.message;
    }
}

async function startRecording() {
    hideStatus();
    resetCapture();
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
            },
        });
        const chunks = [];
        mediaRecorder = new MediaRecorder(mediaStream, chooseRecorderOptions());
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) chunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
            recordedBlob = new Blob(chunks, { type: mediaRecorder.mimeType || chunks[0]?.type || 'audio/webm' });
            mediaStream.getTracks().forEach((track) => track.stop());
            mediaStream = null;
            elements.provisionalTranscriptRow.classList.add('hidden');
            elements.captureActions.classList.remove('hidden');
            elements.captureActions.classList.add('flex');
            elements.recordButton.disabled = true;
            elements.language.disabled = false;
            if (browserTranscript) {
                elements.finalTranscript.textContent = browserTranscript;
            } else {
                elements.finalTranscript.textContent = 'No finalized browser transcript. The backend can still transcribe this recording.';
            }
        };

        recordedAt = new Date().toISOString();
        recordedLanguage = elements.language.value;
        isRecording = true;
        mediaRecorder.start(250);
        startBrowserRecognition();
        timerStartedAt = Date.now();
        updateTimer();
        timerInterval = window.setInterval(updateTimer, 250);
        elements.language.disabled = true;
        elements.recordButton.classList.add('is-recording');
        elements.recordButton.setAttribute('aria-label', 'Stop recording');
        elements.recordLabel.textContent = 'Listening… tap to stop';
        elements.recordHelp.textContent = 'Speak naturally. Fillers and mistakes are useful test data.';
        elements.finalTranscript.textContent = SpeechRecognition
            ? 'Waiting for finalized speech…'
            : 'Browser recognition unavailable. Recording for backend transcription…';
        elements.provisionalTranscriptRow.classList.toggle('hidden', !SpeechRecognition);
        elements.interimTranscript.textContent = 'Listening…';
    } catch (error) {
        showStatus(`Microphone could not start: ${error.message}`, 'error');
        resetRecordingUi();
    }
}

function resetRecordingUi() {
    isRecording = false;
    window.clearInterval(timerInterval);
    timerInterval = null;
    elements.recordButton.classList.remove('is-recording');
    elements.recordButton.setAttribute('aria-label', 'Start recording');
    elements.recordLabel.textContent = 'Tap to speak';
    elements.recordHelp.textContent = 'One utterance per turn · tap again to stop';
}

function stopRecording() {
    if (!isRecording) return;
    resetRecordingUi();
    if (recognition) {
        try {
            recognition.stop();
        } catch (_error) {
            // Recognition may already have ended after a pause.
        }
    }
    if (mediaRecorder?.state !== 'inactive') mediaRecorder.stop();
}

async function parseResponse(response) {
    const payload = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    return payload;
}

function addResultCard(payload, audioBlob, localChecksum) {
    const card = elements.resultTemplate.content.firstElementChild.cloneNode(true);
    card.querySelector('.turn-number').textContent = String(turnNumber);
    card.querySelector('.turn-meta').textContent = `${payload.language} · ${new Date(payload.recorded_at).toLocaleString()}`;

    const audioUrl = URL.createObjectURL(audioBlob);
    audioObjectUrls.push(audioUrl);
    card.querySelector('.turn-audio').src = audioUrl;

    card.querySelector('.browser-result').textContent = payload.browser_transcript || '[No browser transcript]';
    const confidence = Math.round((payload.browser_confidence || 0) * 100);
    card.querySelector('.browser-detail').textContent = `${confidence}% confidence · ${payload.browser_alternatives.length} alternative(s)`;

    const providerResult = card.querySelector('.provider-result');
    const providerDetail = card.querySelector('.provider-detail');
    if (payload.provider.status === 'ok') {
        providerResult.textContent = payload.provider.transcript || '[Empty provider transcript]';
        providerDetail.textContent = `${payload.provider.latency_ms} ms · gpt-transcribe`;
    } else {
        providerResult.textContent = '[Backend transcription unavailable]';
        providerResult.classList.add('text-red-200');
        providerDetail.textContent = `${payload.provider.latency_ms} ms · ${payload.provider.message}`;
    }

    const reference = card.querySelector('.manual-reference');
    const metrics = card.querySelector('.metrics');
    const errorDetails = card.querySelector('.error-details');
    const browserWer = card.querySelector('.browser-wer');
    const providerWer = card.querySelector('.provider-wer');
    const browserErrors = card.querySelector('.browser-errors');
    const providerErrors = card.querySelector('.provider-errors');
    const transportStatus = card.querySelector('.transport-status');
    const transportMatches = payload.browser_transcript === browserTranscript
        && payload.browser_utf8_sha256 === localChecksum;
    transportStatus.textContent = transportMatches ? 'Exact match' : 'Mismatch';
    transportStatus.classList.add(transportMatches ? 'text-teal-200' : 'text-red-200');

    reference.addEventListener('input', () => {
        if (!reference.value) {
            metrics.classList.add('hidden');
            errorDetails.classList.add('hidden');
            return;
        }
        const browserStats = wordErrorStats(reference.value, payload.browser_transcript);
        browserWer.textContent = `${browserStats.wer}%`;
        browserErrors.textContent = `Browser: ${browserStats.missing} missing · ${browserStats.added} added · ${browserStats.changed} changed`;
        if (payload.provider.status === 'ok') {
            const providerStats = wordErrorStats(reference.value, payload.provider.transcript);
            providerWer.textContent = `${providerStats.wer}%`;
            providerErrors.textContent = `OpenAI: ${providerStats.missing} missing · ${providerStats.added} added · ${providerStats.changed} changed`;
        } else {
            providerWer.textContent = 'N/A';
            providerErrors.textContent = 'OpenAI: transcription unavailable';
        }
        metrics.classList.remove('hidden');
        errorDetails.classList.remove('hidden');
    });

    elements.turnResults.prepend(card);
    elements.resultsSection.classList.remove('hidden');
}

async function submitTurn() {
    if (!recordedBlob) return;
    elements.submitTurn.disabled = true;
    elements.discardTurn.disabled = true;
    showStatus('Saving audio and asking the backend to transcribe it…', 'info');

    try {
        const localChecksum = await utf8Sha256(browserTranscript);
        const form = new FormData();
        form.append('session_id', sessionId);
        form.append('turn_id', `turn-${turnNumber}`);
        form.append('language', recordedLanguage);
        form.append('browser_transcript', browserTranscript);
        form.append('browser_alternatives', JSON.stringify(browserAlternatives));
        form.append('browser_confidence', String(browserConfidence));
        form.append('recorded_at', recordedAt);
        form.append('audio', recordedBlob, `turn-${turnNumber}.${fileExtension(recordedBlob.type)}`);

        const response = await fetch('/api/turns', { method: 'POST', body: form });
        const payload = await parseResponse(response);
        addResultCard(payload, recordedBlob, localChecksum);

        turnNumber += 1;
        sessionStorage.setItem('literal-stt-next-turn', String(turnNumber));
        elements.turnCount.textContent = `${turnNumber - 1} ${turnNumber === 2 ? 'turn' : 'turns'}`;
        elements.characterPrompt.textContent = prompts[(turnNumber - 1) % prompts.length];
        showStatus(
            payload.provider.status === 'ok'
                ? 'Turn saved. Replay the audio and add a manual reference below.'
                : 'Turn and audio saved. OpenAI transcription failed; check the API key or provider message below.',
            payload.provider.status === 'ok' ? 'success' : 'error',
        );
        recordedBlob = null;
        elements.captureActions.classList.add('hidden');
        elements.captureActions.classList.remove('flex');
        elements.recordButton.disabled = false;
        elements.finalTranscript.textContent = 'Waiting for speech…';
        elements.interimTranscript.textContent = 'Listening…';
        elements.provisionalTranscriptRow.classList.add('hidden');
    } catch (error) {
        showStatus(`Could not save this turn: ${error.message}`, 'error');
    } finally {
        elements.submitTurn.disabled = false;
        elements.discardTurn.disabled = false;
    }
}

async function deleteCurrentSession() {
    const confirmed = window.confirm('Delete all saved audio and transcript data for this session?');
    if (!confirmed) return;

    elements.deleteSession.disabled = true;
    try {
        const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: 'DELETE' });
        if (response.status !== 404) await parseResponse(response);

        audioObjectUrls.splice(0).forEach((url) => URL.revokeObjectURL(url));
        elements.turnResults.replaceChildren();
        elements.resultsSection.classList.add('hidden');
        sessionId = crypto.randomUUID();
        sessionStorage.setItem('literal-stt-session', sessionId);
        sessionStorage.setItem('literal-stt-next-turn', '1');
        elements.sessionShortId.textContent = sessionId.slice(0, 8);
        turnNumber = 1;
        elements.turnCount.textContent = '0 turns';
        elements.characterPrompt.textContent = prompts[0];
        resetCapture();
        showStatus('The saved session was deleted. A new empty session is ready.', 'success');
    } catch (error) {
        showStatus(`Could not delete the session: ${error.message}`, 'error');
    } finally {
        elements.deleteSession.disabled = false;
    }
}

elements.recordButton.addEventListener('click', () => {
    if (isRecording) stopRecording();
    else startRecording();
});
elements.submitTurn.addEventListener('click', submitTurn);
elements.discardTurn.addEventListener('click', resetCapture);
elements.deleteSession.addEventListener('click', deleteCurrentSession);
window.addEventListener('beforeunload', () => {
    if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
    audioObjectUrls.forEach((url) => URL.revokeObjectURL(url));
});

updateSupportBadge();
