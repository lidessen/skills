---
name: reframe
description: |
  Methodology for designing in territory where the industry is still
  groping for shape — AI-native systems, agent-first interfaces, any
  domain whose category is forming. Strip the target to 3-5 abstract
  functions (the essence), redraw the load-bearing skeleton from the
  new paradigm's primitives, stress-test it without traditional
  crutches, then add familiar flesh as a projection of the new
  skeleton — never the other way around.

  Use when the user is designing something whose conventions don't
  yet exist and where copying the traditional reference design would
  lead them astray. Trigger on phrases like "AI native X", "agent-
  first X", "重新定义 X", "重做 X 但底层换", "reframe X for Y",
  "X 在新范式下应该长什么样", "做一个没有先例的系统", or when the
  user voices the tension between "穿新鞋走老路" and "立得住的新骨架".

  Do NOT trigger for incremental redesigns within an existing
  paradigm (use design-driven), for explanatory writing about a
  paradigm (use technical-article-writing), or for vague "make it AI"
  requests with no concrete domain to redefine.

  Supports arguments: `/reframe init` to set up the project's
  `reframe/` working directory and register the skill in agent
  configs, `/reframe close` to finalize a redefinition with a
  retrospective and archive the working document.
argument-hint: "[init | close]"
---

# Reframe

Methodology for designing in territory where no one yet knows the
shape. When you're building "AI native CRM" or "agent-first IDE", the
danger isn't that you fail outright — it's that you succeed at a
*traditional* version wearing the new paradigm's clothes. New buttons,
old skeleton. The user gets traditional capability with paradigm
overhead: the worst of both worlds.

This skill enforces a sequence designed to prevent that. Distill what
the domain actually does underneath its surface. Redraw the load-
bearing skeleton using the new paradigm's primitives. Test whether the
skeleton stands without traditional crutches. *Then* add the familiar
surface as a projection of the new skeleton.

## Commands

When invoked with an argument, dispatch to the corresponding file:

- `/reframe init` → Read and follow `commands/init.md` in this skill
  directory. First-time project plumbing: create `reframe/`, register
  the skill in agent configs.
- `/reframe close` → Read and follow `commands/close.md` in this skill
  directory. Finalize a redefinition with a retrospective and archive
  the working document.
- No argument → Continue with the methodology below. If `reframe/`
  contains in-progress documents, list them and offer to resume one.
  If empty, ask the user what they want to reframe and create a new
  document from `references/template.md`.

---

## Core idea: skeleton vs flesh

Every domain has two layers, and reframing is about which one you
rebuild first.

- **Skeleton** — the load-bearing abstract functions. For a ticket
  system: information ingestion + state tracking + event notification.
  Three abstract verbs. Survives every UI redesign for thirty years.
- **Flesh** — the surface a user sees. Forms, lists, buttons,
  workflows. Tied to a specific paradigm and era.

Most "AI native" failures rebuild the flesh and call the result
innovation. The skeleton stays a CRUD database with stage fields, and
the agent becomes a smart input box bolted on top. The reframe never
happened.

A real reframe reconstructs the skeleton itself from the new
paradigm's primitives. Flesh follows. Often the user-visible result
*resembles* a traditional system — that's fine, that's the projection
— but every operation underneath flows through new primitives.

## The artifact: `reframe/<target>.md`

A reframe is a multi-session exploration. The document is the
pause-and-resume mechanism: any agent (a future you, a different
session, a teammate) can pick up where work left off because the full
thinking trail lives in the file, not in any session's memory.

One file per redefinition target. Structure follows
`references/template.md`. The agent reads the file at the start of
every session and updates it at the end of every meaningful move.

When the user invokes the skill with no argument:

1. List existing `reframe/*.md` files (non-archived). If any are
   marked `Status: active`, offer them as resume candidates.
2. If the user picks one, load it and continue from its current
   phase. If they want a new target, create a new file from the
   template and start at Phase 1.
3. If no `reframe/` directory exists, suggest `/reframe init` first
   — but if the user prefers to skip plumbing, just create the
   directory and document inline.

---

## Phase 1: Essence Extraction

Strip the target domain to 3-5 abstract functions. The test for an
essence statement: would it still be true thirty years from now,
under any paradigm we can imagine?

Common failure modes when extracting essence:

- **Listing features instead of functions.** "Customer profile,
  pipeline view, reporting dashboard" — those are flesh. The
  underlying function is "remember relationships, track interactions,
  surface opportunities."
- **Smuggling paradigm assumptions.** "User clicks through stages" —
  that's a paradigm artifact (mouse + form). The function underneath
  is "advance state in response to evidence."
- **Compressing too far.** "It's just data management." Too abstract
  to constrain skeleton design.

Calibration: an essence statement should be specific enough that it
*could not* be implemented the wrong way, and abstract enough that it
prescribes no specific implementation. "Track interactions" is too
vague. "Maintain a per-relationship running synthesis updated by every
recorded interaction" is essence-grade — it tells you what must be
possible without saying how.

Write the result under `## Essence` in the document. One sentence per
function, plus one sentence of justification ("why is this essence
rather than artifact?").

## Phase 2: Paradigm Primitives

What does the new paradigm actually offer as building blocks? Be
operationally concrete. Slogans ("AI is native") are not primitives —
the primitives are the operational consequences of the slogan.

For AI-native, primitives might be:

- Every action is exposed as a tool with a JSON schema
- Agents can read arbitrary context (emails, meetings, prior chats)
  rather than only what was typed into a form
- State can be inferred from evidence instead of entered by hand
- Natural language and structured data flow both ways
- Background agents can act between user sessions

Calibration: a primitive must be something a skeleton can *be
expressed in*. If a candidate primitive is still a slogan, drill
down. "AI native" → what does "native" mean operationally? Keep
drilling until the answer is concrete enough to load-bear.

Write the result under `## Paradigm Primitives`. Aim for 4-8
primitives. Fewer than 4 usually means under-specified; more than 8
means some are not load-bearing and can be folded.

## Phase 3: Skeleton Reconstruction

Re-express the essence using the primitives — not "essence with
primitives sprinkled on", but essence *expressed in* primitives end-
to-end.

The hardest discipline: refuse to reach for the traditional shape
when the new shape is unclear. If you find yourself drafting "a deal
table with a stage column", catch yourself — that's old skeleton.
The reframe question is: *what is a deal, in a world where state is
inferred from evidence?* Maybe it's "a relationship trajectory with a
confidence-weighted suggested stage that the user confirms or
overrides." Maybe it's something else entirely. Sit with the
question.

Version explicitly. The first skeleton will be wrong somewhere. Write
v1, run stress tests (Phase 4), write v2 in light of what failed.
Keep v1 visible (collapsed) so the evolution stays legible.

Write under `## Skeleton (vN)` with a short rationale linking each
load-bearing piece back to a primitive. If a piece can't be traced to
a primitive, that's a smell — investigate before continuing.

## Phase 4: Skeleton Stress Test

Probe the skeleton by removing traditional crutches one at a time
and watching what happens:

- "Suppose there are no input forms — can the skeleton still ingest
  what it needs?"
- "Suppose there are no manual stage transitions — does the skeleton
  produce stage state from evidence?"
- "Suppose there are no scheduled reports — does the skeleton surface
  what users need to know without polling?"
- "Suppose the user never logs in for a week — what still happens
  correctly?"

For each crutch removed, three possible outcomes:

1. **Skeleton holds.** New primitives carry the load. Record this —
   it's positive evidence the reframe is real, not cosmetic.
2. **Skeleton bends but holds with adjustment.** Modify the skeleton
   to absorb the load. Bump the version.
3. **Skeleton collapses.** Either essence was misidentified (back to
   Phase 1), primitives are insufficient (back to Phase 2), or this
   particular function genuinely doesn't redefine in the new paradigm
   — it stays traditional, and that's the boundary of the reframe.

Outcome 3 is not failure. Knowing where the new paradigm *doesn't*
help is part of the design. Document the boundary explicitly so it
doesn't get re-litigated later.

Write all stress tests and outcomes under `## Stress Tests`. The
section is append-only history — don't delete failed attempts; their
existence is the evidence that the surviving skeleton was tested.

## Phase 5 (cross-cutting): Transfer Learning

Mature domains have already solved problems isomorphic to the ones
the new domain is groping with. The discipline is: **mine for
patterns, not for shapes**. Translate, don't copy.

Examples of fruitful transfers:

- AI agent context management ↔ software engineering's information
  architecture (L1/L2/L3 layering, just-in-time loading, the
  principle that more context isn't always better)
- Conversation memory across sessions ↔ email threading and version
  control merge semantics
- Tool schema design ↔ API design conventions and Unix pipe
  composability
- Agent attention/budget management ↔ Kanban WIP limits and OS
  scheduler quotas
- Background agent coordination ↔ build system DAGs

For each candidate source domain, ask two questions:

1. What problem did the source domain solve, *abstractly*?
2. Does the new domain face an isomorphic problem?

If yes, the source pattern *seeds* the new design — never as a
verbatim copy. The translation step is where the value lives. Note
deliberate non-transfers too: "considered borrowing X but it relies
on assumption Y that doesn't hold here." Non-transfers prevent
re-considering the same option later.

Transfer is cross-cutting — invoke it during Phase 2 (primitive
identification), Phase 3 (skeleton drafting), Phase 4 (rescue when
the skeleton bends). Write under `## Transfer Log`.

## Phase 6: Flesh

Once the skeleton holds, plan the user-facing surface as a
*projection* of the skeleton. Two rules govern flesh:

- **Familiarity is fine, mimicry is suspicious.** A list view that
  resembles a traditional one is fine *as long as* it's a projection
  of skeleton state. If you can't name which skeleton state it
  projects, it's not flesh — it's old paradigm leaking through, and
  the data behind it is probably in the wrong shape.
- **Flesh never adds capability the skeleton lacks.** If the user
  needs to do X, X must be expressible in the skeleton. If not, the
  right move is to revise the skeleton (back to Phase 3), not to
  bolt X onto the surface. A surface capability the skeleton can't
  reason about will fight the rest of the system forever.

Write under `## Flesh Plan`. For each flesh element, state which
skeleton state it projects and which user need it serves.

---

## Common traps

**穿新鞋走老路 — new shoes, old path.** Skeleton is traditional, the
surface is reskinned with paradigm vocabulary. Detection: try
describing the system without any paradigm-specific verbs. If the
description matches a traditional system in the same domain, the
reframe is cosmetic.

**为新而新 — novelty for novelty's sake.** Skeleton is genuinely new
but does the essence functions worse than the traditional version.
Users get fashionable architecture and worse outcomes. Detection:
walk through each essence function and ask "better, worse, or
sideways for the user?" Sideways is acceptable. Worse means the
reframe has lost the plot.

**Premature flesh.** Drawing UI before the skeleton has settled. The
flesh then constrains skeleton revision — changing the skeleton
breaks the UI, so the team stops changing the skeleton. Skeleton
discipline collapses.

**Shapeless transfer.** Borrowing patterns from mature domains
without translation, ending up with a new-domain system that is
secretly the source domain in disguise. The cure is forcing the
"what does this become *here*?" step before the pattern enters the
skeleton.

**Phantom primitives.** Listing capabilities the new paradigm
*could* offer but the team can't actually access (because the
underlying tech isn't there yet, or the platform doesn't expose it).
Skeleton then load-bears on something that doesn't exist. Calibrate
primitives to what's available, not what's imagined.

---

## When NOT to use this skill

- The domain has clear precedent in the new paradigm (follow the
  precedent; use design-driven instead).
- The change is incremental within an existing paradigm (design-
  driven).
- The user wants to *describe* a paradigm, not design within one
  (technical-article-writing).
- No specific domain — vague "let's build something AI native"
  without a target. Get the user to name the domain first; without
  a target there's no essence to extract.
