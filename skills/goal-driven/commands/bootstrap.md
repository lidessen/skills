# goal-driven:bootstrap — Interview-driven GOAL.md

Create the initial `goals/GOAL.md` by interviewing the human. Use when
adopting goal-driven on a project that doesn't have one yet — or when
re-setting after a major change in direction.

Bootstrap handles plumbing idempotently — fine to run without having run
`/goal-driven init` first. If directories or stub files are missing, set
them up in Phase 4.

The interview is the whole point. Do **not** draft GOAL.md alone in your
head, ask "approve?", and write the file. Section by section, asking,
echoing, getting confirmation, then moving on. The point is that the human
ends up owning the compass — the agent is the writer, not the author.

Work in four phases: **Prepare → Interview → Draft → Wire up**.

## Phase 1 — Prepare

### 1.1 Check current state

If `goals/GOAL.md` already has non-stub content, stop and ask the human:

- "There's already content in `goals/GOAL.md` — do you want to redo from
  scratch (I'll archive the current one), or did you mean
  `/goal-driven audit` to refresh it?"

If they confirm redo: move existing `goals/GOAL.md` to
`goals/GOAL.archived-YYYY-MM-DD.md` before continuing.

### 1.2 Surface what's already known

If there's prior context — `README.md`, project notes, prior conversation,
emails, an existing scratch document — read it. The interview is faster
when the agent can ask "I see in your notes that X — is that the north
star, or a means to it?" rather than starting blank.

If the project is new with no prior writing, skip this; start the
interview from zero.

## Phase 2 — Interview

Four sections, in order. Do not skip ahead. Each section ends only when
the human has confirmed the wording the agent will write into the file.

### 2.1 North star (what should be true when this is done)

Ask: "In one or two sentences, what should be true when this initiative is
done? What's the world-state you're aiming at?"

Listen for:
- Specific outcome (good): "users can find old conversations by meaning,
  not just keywords"
- Activity description (warning): "build a semantic search system" — that's
  a means, not an end. Push: "And what does that enable for the user?"
- Vague aspiration (warning): "improve search". Push: "Improve how, for
  whom, by what measure?"

Echo back: "I'll write the north star as: '<wording>'. OK?" Wait for
confirmation. If they edit, echo the edit. Do not move on until they say
yes.

### 2.2 Success criteria (how you'd know it's done)

Ask: "How would you know this is done? What would you measure or observe?"

Push every soft answer toward something falsifiable:

- "Users like it" → "Like it how? Daily-active count? Survey score? Repeat
  usage of the new feature?"
- "It's fast enough" → "Fast enough = what? P50? P95? Under what number?"
- "We learn enough" → "Learn what specifically? What question would we be
  able to answer that we can't now?"

If a criterion really is soft (e.g., "the team feels less burned out"),
require a paired proxy indicator: "oncall pages per week", "voluntary
overtime hours", "self-reported energy at end-of-week retro". A criterion
without a way to observe it is decoration. Either find a proxy or cut it.

Aim for **2–5 criteria.** More than that is usually a sign that some are
secretly path-level (how) rather than goal-level (what).

Number them stably as `C1, C2, C3, ...` in the order confirmed. **These IDs
never get reused** — if C2 is later retired, C2 stays in GOAL.md as
retired; new criteria become C5, C6, etc.

Echo each criterion back individually, with its measurement: "C2 will
read: 'P95 latency under 500ms, measured on production traffic replay.'
OK?" One at a time.

### 2.3 Invariants (what must stay true regardless of path)

Ask: "What must stay true regardless of how we get there? Things that are
non-negotiable, even if they slow us down or rule out clever shortcuts."

Examples to prompt with:
- "User data doesn't leave the local database"
- "We don't add new always-on infrastructure"
- "I don't work weekends"
- "We only support contracts; no scope creep"

Invariants differ from criteria: criteria are achieved at the end;
invariants must hold every step of the way. Violating an invariant is a
STOP signal even if criteria are on track.

Aim for **0–4 invariants.** If there are more, some are probably criteria
or non-goals in disguise.

### 2.4 Non-goals (what's tempting but isn't success)

Ask: "What's tempting to call success but isn't? What might look like
progress but actually isn't? What did you almost include that you decided
to leave out?"

Non-goals are the quiet defense against scope creep. Common patterns:

- Anything that's a possible "phase 2" — name it as a non-goal, not a
  delayed goal
- Adjacent improvements that the team will be tempted to make along the
  way
- Metrics that will go up as a side effect but aren't the point

Echo each non-goal back. Confirm.

## Phase 3 — Draft

Now, and only now, write `goals/GOAL.md` using the format in
`../references/templates.md`. The file is just a transcript of what the
human confirmed in the interview, structured. No new claims should appear
in the file that didn't come from the interview.

After writing, show the file in chat: "Wrote `goals/GOAL.md`. Final
version below — say if anything looks off."

This is a final check, not a review — by Phase 3 the content has been
confirmed three times (during interview, during echo, as you wrote). The
final read catches typos and ordering issues, not substance.

## Phase 4 — Wire up

### 4.1 Ensure plumbing exists

If missing (idempotent — skip what's already there):

- `goals/` directory
- `goals/OPEN-STOPS.md` (with empty list — see template)
- `goals/journal-YYYY-MM.md` for the current month (heading only)

### 4.2 Update agent configs

Append goal-driven instructions to agent config files (CLAUDE.md,
.cursorrules, AGENTS.md, etc.) — see `init.md` Step 2 for the snippet and
the list of common config locations. Reuse that content; don't re-derive.

If the human ran `/goal-driven init` previously, configs are already
updated — verify and skip.

### 4.3 First journal entry

Add a "kickoff" entry to the current month's journal. Format:

```markdown
## YYYY-MM-DD — Kickoff
- What I did: bootstrapped GOAL.md via interview.
- Observations: north star confirmed; <N> success criteria; <M> invariants.
- Criteria check: all unclear — no work done yet.
- Judgment: no change. Next session begins real work.
```

This anchors the journal so the next session has something to read.

### 4.4 Commit

Commit `goals/`, agent config updates, and any hook configs together as
the goal-driven setup. One commit, clear message: "goal-driven: bootstrap
GOAL.md and journal scaffolding".

### 4.5 Tell the human what's next

- The compass is set. From now on, every work session ends with a journal
  entry the agent will draft and ask them to confirm.
- If a criterion fails or the north star feels wrong, the agent will STOP
  and ask before continuing.
- They don't need to remember any of this — the agent's protocol carries
  it. Their job is to approve, redirect, and decide at STOPs.

## Avoid these failure modes

**Drafting before interviewing.** Tempting because the agent has a guess.
Don't. The interview's purpose is the human's commitment to the wording —
a draft you wrote and they nodded at is not the same as a wording they
confirmed phrase by phrase.

**Letting soft criteria slide.** "We'll know it when we see it" sounds
human and accommodating. It's also exactly the criterion that will be
silently treated as `✓` in every future session. Push for falsifiability
or a proxy. If the human resists, name the tradeoff explicitly: "Without
a proxy, I won't know when to STOP. Are you OK with that?"

**Listing too many criteria.** If you end up with 8, some are path-level.
Ask: "Would this still feel achieved if we did the others but missed
this one?" If yes, it's probably a path detail. If "achieved" depends on
all 8 simultaneously, the goal is too compound — split or reframe.

**Skipping non-goals.** The human will say "I don't have any non-goals".
They do; they just haven't named them. Prompt with: "What did you almost
include but decided to leave out? What would be a sign of scope creep
later?"
