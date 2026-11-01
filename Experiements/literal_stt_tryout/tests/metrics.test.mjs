import test from 'node:test';
import assert from 'node:assert/strict';

import {
    normalizeWords,
    utf8Sha256,
    wordErrorRate,
    wordErrorStats,
} from '../static/metrics.mjs';


test('normalizeWords ignores case and punctuation but preserves repetition', () => {
    assert.deepEqual(
        normalizeWords('Um, EU eu fui ontem.'),
        ['um', 'eu', 'eu', 'fui', 'ontem'],
    );
});

test('wordErrorRate counts a missing repeated word as an error', () => {
    assert.equal(
        wordErrorRate('Um, eu eu fui ontem.', 'um eu fui ontem'),
        20,
    );
});

test('wordErrorRate handles empty references without dividing by zero', () => {
    assert.equal(wordErrorRate('', ''), 0);
    assert.equal(wordErrorRate('', 'invented words'), 100);
});

test('utf8Sha256 fingerprints the exact untrimmed Unicode transcript', async () => {
    assert.equal(
        await utf8Sha256('  eu, eu fui no café ontem... não hoje 😅  '),
        'eba89f619d701952ad6947150b3a45e040869e855ffce9a65cbaf33592a74c1c',
    );
});

test('wordErrorStats distinguishes missing, added, and changed words', () => {
    assert.deepEqual(wordErrorStats('um eu eu fui', 'um eu fui'), {
        wer: 25,
        missing: 1,
        added: 0,
        changed: 0,
    });
    assert.deepEqual(wordErrorStats('eu fui', 'eu realmente fui'), {
        wer: 50,
        missing: 0,
        added: 1,
        changed: 0,
    });
    assert.deepEqual(wordErrorStats('eu fui', 'eu foi'), {
        wer: 50,
        missing: 0,
        added: 0,
        changed: 1,
    });
});
