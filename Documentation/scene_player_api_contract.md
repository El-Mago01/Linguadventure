# LinguAdventure — scene player API interface (proposed)

This is an **interface contract**, not a backend implementation. Existing backend endpoints must be adapted to match. `attempt_id` is a persistent identifier; `attempt_number` is a user-facing ordinal.

## GET `/play_scene/<adventure_id>/<scene_id>`

Returns the Jinja scene-player HTML. No change.

## GET `/api/play_scene/<adventure_id>/<scene_id>`

Returns the scene and persona fields already used by the current player, plus:

```json
{
  "scene": {"title": "At the Café", "goal": "Order a drink"},
  "persona": {"name": "Sofia", "image_url": null},
  "can_play": true,
  "attempt_id": 42,
  "attempt_number": 2,
  "turns": [{"role": "student", "text": "Olá", "correction": "Olá!"}],
  "scene_completed": false
}
```

For a completed latest attempt, return `scene_completed: true`, its saved `turns`, the saved `feedback`, `next_scene_id`, and `next_scene_unlocked` (Boolean). The frontend renders the saved conversation read-only and displays the evaluation. For a scene never attempted, `attempt_id` may be null, `turns` empty, and `scene_completed` false. The backend must establish an initial attempt before processing the first turn (e.g. automatically on the first PUT).

## PUT `/api/play_scene/<adventure_id>/<scene_id>`

Existing text JSON `{ "message": "..." }` and voice multipart `audio` remain unchanged. Backend identifies the current active attempt from the authenticated session or its own storage, and appends the turn to it. Return:

```json
{
  "student_turn": {"role": "student", "text": "Eu quero café", "correction": "Eu queria um café, por favor."},
  "persona_turn": {"role": "persona", "text": "Claro! Até à próxima!", "audio_url": null},
  "scene_completed": true,
  "next_scene_id": 3,
  "next_scene_unlocked": true,
  "feedback": {
    "summary": "You achieved your goal.",
    "goal_achieved": true,
    "estimated_level": "A2",
    "words_used": ["café", "obrigado"],
    "phrases_well": ["Quanto custa?"],
    "phrases_to_improve": ["Eu quero → Eu queria"],
    "grammar_tips": ["Use queria for polite requests."],
    "practice_next": "Practice polite ordering."
  }
}
```

For ordinary turns, `scene_completed` is false and feedback may be omitted. On the final turn, generate the persona's natural closing reply, evaluate the scene, persist the completed attempt and feedback, and only then return `scene_completed: true`. **A goal achieved is not a language pass/fail test.** Prevent further PUTs to a completed attempt on the server.

## POST `/api/play_scene/<adventure_id>/<scene_id>/attempts`

Starts a **new** attempt and returns:

```json
{
  "attempt_id": 43,
  "attempt_number": 3,
  "persona_turn": {"role": "persona", "text": "Bom dia!"}
}
```

The frontend clears the currently displayed transcript and evaluation **only after this request succeeds**, and then displays the new attempt. Existing completed attempts are retained. The frontend does not yet implement browsing previous attempts. The backend must handle any existing in-progress attempt consistently (reuse or replace/abandon it), enforce authorization and scene access, and avoid creating duplicates on repeated requests.

## Important lifecycle choices

- The initial attempt can be created on first PUT; a retake is created explicitly with POST `/attempts`.
- GET is read-only and does not create attempts.
- The existing POST `/complete` is no longer used by the updated frontend; remove it only after the backend migration.
- Next-scene unlock is a backend authorization decision, not just a frontend button.
- No new previous-attempt browsing route is defined yet.
- CSRF protection is deferred for the learning POC, but must be enabled before production deployment.
