# LinguAdventure

**Learn a language by living the story.**

LinguAdventure is an AI-powered conversational language-learning application in which the learner participates in an interactive spoken adventure. 
Instead of completing isolated exercises, the learner uses the target language to communicate with AI-controlled characters, solve situations, make decisions, 
and progress through an ongoing story.

The central idea is simple: **the learner should want to return because they want to know what happens next — 
not because the application sends a reminder.**

> **Project status:** AI Engineering study project / prototype under development.

---

## Project Objective

LinguAdventure explores how generative AI, speech technology, persistent memory, and adaptive learner modelling can be combined to 
create an engaging spoken-language learning experience.

The first version focuses on:

- **Support language:** English
- **Target language:** Portuguese
- **Interaction:** primarily spoken conversation
- **Format:** adventures consisting of approximately 4–8 scenes per adventure
- **Session length:** short runs of roughly five minutes
- **Adaptation:** future interactions are influenced by the learner's previous performance

The architecture is intended to support additional languages and adventures later.

---

## Problem Definition

The project is built around two main questions:

1. **How might we help a learner practise speaking and understanding a new language in a fun and effective way?**
2. **How might we maintain the learner's attention so that they voluntarily continue learning without relying on reminders?**

LinguAdventure addresses these questions by embedding language practice inside an interactive story. Speaking and understanding the target language becomes necessary to progress through the adventure.

---

## How It Works
A learner lands on the side and registers name, age, sex, email, language to learn.

A learner selects an adventure and enters a story containing several scenes and AI-controlled personas.

A typical interaction follows this flow:

```text
Learner speaks
      ↓
Speech-to-Text
      ↓
Language / context analysis
      ↓
Learner state + Adventure state
      ↓
LLM generates persona response
      ↓
Text-to-Speech
      ↓
Learner hears the character
```

The AI does not simply answer as a generic language tutor. It plays a specific character with a defined personality, knowledge, 
motivation, mood, and role in the current scene.

For example, a character may be serious, humorous, impatient, warm, reserved, or mildly flirtatious. 
The character should remain consistent while still adapting the linguistic complexity of the conversation to the learner.

---

## Adventures and Scenes
An adventure contains approximately **4–8 scenes** connected by an overall storyline.
An adventure defines **what happens**, but it does not have a fixed language level.
An A1 learner and a B2 learner can encounter the same real-life situation; the AI adapts the language and 
conversational complexity to the individual learner.

Each scene can define:

- location and setting
- detailed scene description
- involved personas
- starting situation
- narrative objective
- information that must be discovered
- events that must, may, or must not happen
- required ending state
- transition to the next scene
- cliff-hanger
- language-learning opportunities

The scene specification provides narrative guardrails while leaving the actual dialogue dynamic.

### Example

A learner has lost a backpack and returns to a café to look for it.

The scene may specify that the café employee eventually remembers seeing another traveller leave with a similar backpack. The AI is free to conduct the conversation naturally, but it must not reveal information the character does not know or resolve the entire adventure prematurely.

---

## Personas

Personas are reusable AI-controlled characters.

A persona can contain:

- name and role
- background
- personality
- speaking style
- behavioural traits
- preferred language/register
- voice configuration
- general knowledge

Personality traits may also be represented structurally, for example:

```text
Humorous:     8/10
Serious:      3/10
Patient:      8/10
Flirtatious:  5/10
Talkative:    7/10
Helpful:      9/10
```

A persona's behaviour can change within a particular scene. A normally humorous character may, for example, be worried or unusually serious because of the current situation.

The project therefore distinguishes between the **persona** and the **persona-in-scene state**.

---

## Progressive Information Disclosure

Characters should not immediately reveal everything they know.

A scene can define an information-disclosure sequence so that information emerges naturally during the conversation.

For example:

```text
1. The character remembers the learner.
2. The character remembers another person sitting nearby.
3. The character recalls a similar backpack.
4. The character remembers that the person left in a taxi.
5. The character finally remembers knowing the taxi driver.
```

This helps control pacing and prevents the LLM from solving an entire scene in a single response.

The system can distinguish between:

- **Knowledge** — facts the persona knows
- **Beliefs** — what the persona thinks may be true
- **Unknown information** — facts the persona must not claim to know

---

## Adaptive Learner Model

LinguAdventure maintains an evolving learner model rather than treating every conversation as independent.

Potential learner information includes:

- estimated CEFR level
- speaking and comprehension ability
- vocabulary demonstrated
- recently introduced vocabulary
- grammar strengths
- recurring mistakes
- areas requiring additional practice
- use of the support language
- progress across sessions

The overall CEFR level is only one signal. A learner could, for example, be relatively strong in travel vocabulary while still struggling with past tense or prepositions.

The system can therefore adapt at a more granular level than simply selecting an A1, A2, or B1 conversation.

---

## Invisible Adaptive Learning

A core design principle is that identified weaknesses should influence future story interactions **without unnecessarily turning the adventure into a traditional exercise**.

For example, if the system detects difficulty with numbers, a later scene might naturally require the learner to understand a price or departure time.

If the learner struggles with past tense, a character might ask what happened earlier that day.

```text
Conversation
     ↓
Performance analysis
     ↓
Learner model update
     ↓
Future learning objective
     ↓
Next story scene creates a natural practice opportunity
```

The story therefore provides the context in which targeted learning occurs.

---

## Feedback and Progress

The learner receives feedback on spoken-language performance while preserving the flow of the conversation.

Not every small mistake needs to interrupt the story. The system can distinguish between errors that require immediate clarification and errors that can be recorded for later feedback.

After a run, the learner receives a short progress review containing information such as:

- strengths
- recurring mistakes
- new vocabulary
- areas requiring additional practice
- progress compared with previous sessions
- suggested learning objectives for the next run

The resulting assessment is stored and used when constructing subsequent interactions.

---

## Two Types of Memory

LinguAdventure separates **learning memory** from **story memory**.

### Learning memory

Answers questions such as:

- What does this learner already know?
- What does the learner struggle with?
- Which vocabulary has already been encountered?
- What should be practised next?

### Story memory

Answers questions such as:

- What has happened so far?
- Which characters has the learner met?
- What decisions were made?
- Where is the learner currently located?
- Which story elements remain unresolved?
- What was the latest cliff-hanger?

Both forms of state are used to construct the context for the next AI interaction.

---

## Adventure Continuity

The learner can stop an adventure and continue later.

The application stores the current adventure and scene state so that the next run can resume from the appropriate point rather than starting a new conversation.

Short sessions should ideally end with an unresolved event or **cliff-hanger** that provides a natural reason to return.

---

## AI Engineering Components

The project is intended to demonstrate several AI Engineering capabilities rather than functioning only as an LLM wrapper.

### Large Language Model

Used for:

- dynamic dialogue
- persona role-play
- story progression
- language analysis
- learner feedback
- adaptation of language complexity
- generation of contextually relevant learning opportunities

### Speech-to-Text

Converts the learner's spoken input into text for conversational and language analysis.

### Text-to-Speech

Converts persona responses into speech. Different personas may use different voices where supported by the selected speech technology.

### Structured LLM Output

Selected AI operations should return validated structured data rather than only free-form text, for example:

```json
{
  "strengths": ["travel vocabulary"],
  "weaknesses": ["past tense"],
  "new_vocabulary": ["bilhete", "comboio", "estação"],
  "next_learning_objectives": [
    "practise describing past events"
  ]
}
```

### Dynamic Context / Prompt Construction

The runtime context can be assembled from:

- persona definition
- persona-in-scene state
- scene description
- narrative constraints
- learner profile
- recent learner performance
- current learning objectives
- adventure history

This allows the same scene to behave differently for different learners without creating separate adventures for each CEFR level.

---

## Data Model

The planned data structure separates the major concepts of the application.
The overview of the data structure can be found here:
https://dbdiagram.io/d/table_scheme-6aa2bec5fa3334712c04197b

Important entities currently considered include:

- `students`
- `adventures`
- `scenes`
- `personas`
- `scene_personas`
- `student_adventures`
- `sessions`
- `interactions`
- `language_feedback`
- `session_reviews`
- `skills`
- `student_skills`
- `learning_objectives`

The `scene_personas` relationship is particularly important because a persona's mood, motivation, knowledge, and behaviour can differ between scenes.

---

## Adventure Authoring

Adventures are designed using a structured **Adventure Design Document** rather than a traditional fixed screenplay.

A conventional screenplay defines what characters say. LinguAdventure instead defines:

- what characters know
- what they believe
- what they want
- how they behave
- what must happen in the scene
- what must not happen
- where the scene needs to end

The LLM dynamically generates the actual dialogue within these constraints.

A future authoring workflow could be:

```text
Adventure Design Document
          ↓
LLM extraction
          ↓
Structured JSON
          ↓
Schema validation
          ↓
Database
          ↓
Runtime prompt/context builder
```

---

## MVP / Definition of Done

The first project milestone is intentionally limited to **one fully functioning adventure**.

The MVP is complete when a learner can:

1. create or load a learner profile;
2. start an adventure;
3. enter and complete a scene/run;
4. communicate verbally with an AI-controlled persona;
5. receive spoken responses in Portuguese;
6. experience language adapted to their ability;
7. receive useful language feedback;
8. complete a short learning run;
9. receive a progress review;
10. have progress and adventure state persisted;
11. leave and later continue the adventure; and
12. start a subsequent run that demonstrably uses information learned about the student during the previous run.

The ability to demonstrate **adaptation between two consecutive runs** is a key success criterion.

---

## Evaluation

The prototype should be evaluated technically as well as functionally.

Potential evaluation areas include:

- **Language adaptation:** Does generated language appropriately match the learner state?
- **Error detection:** Does the system correctly identify relevant learner mistakes?
- **Adaptive behaviour:** Does a weakness detected in one run influence a later run?
- **Story continuity:** Does the system preserve important facts between sessions?
- **Persona consistency:** Does a persona maintain the intended character and behaviour?
- **Narrative compliance:** Does the LLM respect must/may/must-not-happen constraints?
- **Speech recognition:** How reliably is learner speech transcribed?
- **Latency:** Is the speech-to-response delay acceptable for conversation?
- **Structured-output reliability:** Can AI-generated assessments be validated and stored consistently?

---

## Possible Future Extensions

Potential extensions after the MVP include:

- automatic initial CEFR assessment
- multiple adventures
- additional target languages
- richer persona voices
- pronunciation assessment
- detailed vocabulary tracking
- progress dashboard
- spaced repetition embedded into stories
- dynamic adventure branching
- learner-selected themes
- generated visual environments or characters
- comparison of different LLMs
- local LLM support
- quantized-model deployment
- experimentation with different prompting and memory strategies

---

## Central Engineering Question

> **How can generative AI, speech technologies, persistent learner modelling, and interactive storytelling be combined to create an adaptive spoken-language learning experience?**

A more focused experimental question is:

> **Can language weaknesses identified during one conversational episode be used to adapt a subsequent story episode so that the learner naturally encounters opportunities to practise those weaknesses?**

---

## Why LinguAdventure?

LinguAdventure is based on the idea that language is learned for a purpose: to communicate, understand other people, and get things done in real situations.

The application therefore aims to move from:

```text
Learn the language → complete an exercise
```

towards:

```text
Enter the story → need the language → communicate → progress
```

**The language is not the adventure. The language enables the adventure.**
