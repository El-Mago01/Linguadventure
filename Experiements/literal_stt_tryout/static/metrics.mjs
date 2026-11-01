export function normalizeWords(text) {
    return text
        .normalize('NFKC')
        .toLocaleLowerCase()
        .replace(/[^\p{L}\p{N}'’]+/gu, ' ')
        .trim()
        .split(/\s+/u)
        .filter(Boolean);
}

export function wordErrorRate(reference, hypothesis) {
    return wordErrorStats(reference, hypothesis).wer;
}

export async function utf8Sha256(text) {
    const bytes = new TextEncoder().encode(text);
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export function wordErrorStats(reference, hypothesis) {
    const expected = normalizeWords(reference);
    const actual = normalizeWords(hypothesis);

    if (expected.length === 0) {
        return {
            wer: actual.length === 0 ? 0 : 100,
            missing: 0,
            added: actual.length,
            changed: 0,
        };
    }

    const matrix = Array.from(
        { length: expected.length + 1 },
        () => Array(actual.length + 1).fill(0),
    );
    for (let row = 0; row <= expected.length; row += 1) matrix[row][0] = row;
    for (let column = 0; column <= actual.length; column += 1) matrix[0][column] = column;

    for (let row = 1; row <= expected.length; row += 1) {
        for (let column = 1; column <= actual.length; column += 1) {
            const substitutionCost = expected[row - 1] === actual[column - 1] ? 0 : 1;
            matrix[row][column] = Math.min(
                matrix[row - 1][column] + 1,
                matrix[row][column - 1] + 1,
                matrix[row - 1][column - 1] + substitutionCost,
            );
        }
    }

    let row = expected.length;
    let column = actual.length;
    let missing = 0;
    let added = 0;
    let changed = 0;

    while (row > 0 || column > 0) {
        if (
            row > 0
            && column > 0
            && expected[row - 1] === actual[column - 1]
            && matrix[row][column] === matrix[row - 1][column - 1]
        ) {
            row -= 1;
            column -= 1;
        } else if (row > 0 && matrix[row][column] === matrix[row - 1][column] + 1) {
            missing += 1;
            row -= 1;
        } else if (column > 0 && matrix[row][column] === matrix[row][column - 1] + 1) {
            added += 1;
            column -= 1;
        } else {
            changed += 1;
            row -= 1;
            column -= 1;
        }
    }

    const totalErrors = missing + added + changed;
    return {
        wer: Number(((totalErrors / expected.length) * 100).toFixed(1)),
        missing,
        added,
        changed,
    };
}
