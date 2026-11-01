import test from 'node:test';
import assert from 'node:assert/strict';


class FakeClassList {
    constructor() {
        this.classes = new Set();
    }

    add(...classes) {
        classes.forEach((className) => this.classes.add(className));
    }

    remove(...classes) {
        classes.forEach((className) => this.classes.delete(className));
    }

    contains(className) {
        return this.classes.has(className);
    }

    toggle(className, force) {
        if (force ?? !this.classes.has(className)) this.classes.add(className);
        else this.classes.delete(className);
    }
}


class FakeElement {
    constructor() {
        this.classList = new FakeClassList();
        this.disabled = false;
        this.listeners = new Map();
        this.textContent = '';
    }

    addEventListener(type, listener) {
        this.listeners.set(type, listener);
    }

    setAttribute() {}

    async click() {
        await this.listeners.get('click')?.();
    }
}


async function loadApp() {
    const elements = new Map();
    const elementFor = (selector) => {
        if (!elements.has(selector)) elements.set(selector, new FakeElement());
        return elements.get(selector);
    };
    elementFor('#final-transcript');
    elementFor('#provisional-transcript-row');

    class FakeSpeechRecognition {
        static instances = [];

        constructor() {
            FakeSpeechRecognition.instances.push(this);
        }

        start() {}

        stop() {}

        emitFinal(transcript) {
            const result = [{ transcript, confidence: 0.8 }];
            result.isFinal = true;
            this.onresult({ resultIndex: 0, results: [result] });
        }

        emitInterim(transcript) {
            const result = [{ transcript, confidence: 0 }];
            result.isFinal = false;
            this.onresult({ resultIndex: 0, results: [result] });
        }

        emitError(error) {
            this.onerror({ error });
        }
    }

    class FakeMediaRecorder {
        static isTypeSupported() {
            return true;
        }

        constructor() {
            this.mimeType = 'audio/webm;codecs=opus';
            this.state = 'inactive';
        }

        start() {
            this.state = 'recording';
        }

        stop() {
            this.state = 'inactive';
            this.onstop?.();
        }
    }

    const storage = new Map();
    globalThis.document = { querySelector: elementFor };
    globalThis.sessionStorage = {
        getItem: (key) => storage.get(key) ?? null,
        setItem: (key, value) => storage.set(key, value),
    };
    Object.defineProperty(globalThis, 'navigator', {
        configurable: true,
        value: {
            mediaDevices: {
                getUserMedia: async () => ({
                    getTracks: () => [{ stop() {} }],
                }),
            },
        },
    });
    globalThis.MediaRecorder = FakeMediaRecorder;
    globalThis.window = {
        SpeechRecognition: FakeSpeechRecognition,
        MediaRecorder: FakeMediaRecorder,
        addEventListener() {},
        clearInterval() {},
        setInterval: () => 1,
    };

    await import(`../static/app.js?test=${crypto.randomUUID()}`);

    return { elements, FakeSpeechRecognition };
}


test('a recording session requests continuous browser recognition', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();

    await elements.get('#record-button').click();

    assert.equal(FakeSpeechRecognition.instances.length, 1);
    assert.equal(FakeSpeechRecognition.instances[0].continuous, true);
});


test('browser recognition restarts when it ends during an active recording', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].onend?.();

    assert.equal(FakeSpeechRecognition.instances.length, 2);
});


test('speech recognized after a restart is appended to the earlier transcript', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].emitFinal('first phrase');
    FakeSpeechRecognition.instances[0].onend();
    FakeSpeechRecognition.instances[1].emitFinal('second phrase');

    assert.equal(
        elements.get('#final-transcript').textContent,
        'first phrase second phrase',
    );
});


test('an interim result appears only in the provisional transcript', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].emitInterim('a changing guess');

    assert.equal(elements.get('#interim-transcript').textContent, 'a changing guess');
    assert.equal(
        elements.get('#provisional-transcript-row').classList.contains('hidden'),
        false,
    );
    assert.equal(
        elements.get('#final-transcript').textContent,
        'Waiting for finalized speech…',
    );
});


test('a revised interim result replaces only the provisional hypothesis', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].emitInterim('first guess');
    FakeSpeechRecognition.instances[0].emitInterim('revised guess');

    assert.equal(elements.get('#interim-transcript').textContent, 'revised guess');
    assert.equal(
        elements.get('#final-transcript').textContent,
        'Waiting for finalized speech…',
    );
});


test('a final result updates finalized text and clears the provisional hypothesis', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].emitInterim('first guess');
    FakeSpeechRecognition.instances[0].emitFinal('settled words');

    assert.equal(elements.get('#final-transcript').textContent, 'settled words');
    assert.equal(elements.get('#interim-transcript').textContent, 'Listening…');
});


test('a fatal recognition error does not create a restart loop', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    await elements.get('#record-button').click();

    FakeSpeechRecognition.instances[0].emitFinal('settled words');
    FakeSpeechRecognition.instances[0].emitError('not-allowed');
    FakeSpeechRecognition.instances[0].onend();

    assert.equal(FakeSpeechRecognition.instances.length, 1);
    assert.equal(elements.get('#final-transcript').textContent, 'settled words');
    assert.equal(
        elements.get('#interim-transcript').textContent,
        'Browser recognition: not-allowed. Audio is still being recorded.',
    );
});


test('browser recognition stays stopped after the user stops recording', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    const recordButton = elements.get('#record-button');
    await recordButton.click();
    const firstRecognition = FakeSpeechRecognition.instances[0];

    await recordButton.click();
    firstRecognition.onend();

    assert.equal(FakeSpeechRecognition.instances.length, 1);
});


test('stopping recording hides provisional text and keeps finalized text', async () => {
    const { elements, FakeSpeechRecognition } = await loadApp();
    const recordButton = elements.get('#record-button');
    await recordButton.click();
    FakeSpeechRecognition.instances[0].emitFinal('words to keep');
    FakeSpeechRecognition.instances[0].emitInterim('unfinished guess');

    await recordButton.click();

    assert.equal(elements.get('#final-transcript').textContent, 'words to keep');
    assert.equal(
        elements.get('#provisional-transcript-row').classList.contains('hidden'),
        true,
    );
});
