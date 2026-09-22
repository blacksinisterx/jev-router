# LinkedIn post draft — JevRouter

**Attach:** `demo.gif` as the primary media.

---

Second one in a small series exploring Jev (TypeSafe AI's new decision model) as an actual architectural component — this time for LLM routing.

The problem: most "multi-model routing" I've seen is either hardcoded (if task contains "code" → GPT-X) or just sends everything to the biggest model because routing logic is annoying to build well. Both are wasteful in different directions.

**JevRouter** asks Jev four questions about every incoming task, in parallel, in one call:
→ how complex is this (a 5-level rubric, not a binary)
→ what type of task is it (factual / code / creative / reasoning / etc.)
→ does it actually need multi-step reasoning, or just direct generation
→ is this interactive (latency matters) or batch-tolerant

Then a tier policy picks the cheapest model in a small catalog that can actually handle it — escalating up only when the task genuinely needs it.

The part I found interesting building this: complexity and "needs reasoning" aren't the same axis. A code-generation task landed at moderate complexity but didn't need heavy reasoning → routed to a balanced-tier model. A word-problem at the same complexity score *did* flag reasoning_required → got escalated to the frontier tier regardless of its complexity number. A naive "complexity score → tier" mapping would've missed that distinction entirely.

The GIF shows three tasks routing to three different tiers, each with a live cost comparison against what every other tier in the catalog would've cost for the same prompt.

Built the same way as the first project in this series (JevGuard): FastAPI + Vite/React/shadcn, runs at zero cost by default (mock provider matches Jev's real response schema, so a live key is a one-line env change), no real downstream model calls — it only decides which one *would* be used.

Repo + write-up: [link]

#AI #LLMOps #ModelRouting #BuildInPublic

---

**Notes for posting:**
- Swap `[link]` once the repo is pushed.
- Could pair well as a follow-up comment/reply to the JevGuard post rather than a fully separate post, if you'd rather build a visible thread/series on your profile.
