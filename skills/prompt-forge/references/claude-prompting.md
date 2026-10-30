# Prompting Claude (sub-agents, sessions, `claude -p`, Claude in Chrome)

Distilled from Anthropic's "Prompting best practices" page (platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), read 2026-10-27. The page covers the current Fable, Mythos, Opus, Sonnet and Haiku 5.x models and has a separate page per model. Read the page for the target model when model-specific behaviour matters.

## Core rules
1. **Clear and direct.** Write as if for a capable new colleague with no context. The page's test: would a colleague with minimal context be confused by it? Then Claude will be too.
2. **Give the reason.** A constraint with its reason generalises better ("read aloud by TTS, so spell numbers out") than a bare NEVER.
3. **Say what to do, not only what to avoid.** "Write flowing prose paragraphs" works better than "no markdown".
4. **Ask for action explicitly.** "Can you suggest changes" gets suggestions. "Change this function to..." gets changes.
5. **Examples steer format and tone.** 3-5 examples, relevant and varied, wrapped in `<example>` tags inside `<examples>`.
6. **XML tags for mixed content.** `<instructions>`, `<context>`, `<input>`, `<documents>` with `<document index="n">`, `<source>` and `<document_content>`. Keep tag names consistent.
7. **Long inputs at the top, question at the end.** The page reports up to 30% better answers with the query last on long, multi-document input.
8. **Match the prompt's style to the output you want.** A markdown-heavy prompt gets markdown back.
9. **Role in one sentence** when expertise or perspective changes the result; skip it otherwise.

## Thinking and effort
- Current models use adaptive thinking with an effort setting. Do not hardcode thinking budgets; on 4.7 and later `budget_tokens` is rejected.
- Never ask for hidden reasoning. Ask for conclusion, assumptions, evidence and checks.
- Over-thinking: tell it to pick an approach and commit, revisiting only on new contradicting information. Or lower effort.

## Agentic work
- **Scope:** only make changes that were asked for or are clearly necessary; no extra files, abstractions or features.
- **Reversibility:** local, reversible actions are fine; ask before destructive, hard-to-reverse or externally visible ones (delete, force-push, send, post).
- **No guessing about code:** read the file before making claims about it.
- **No hardcoding to pass tests:** solve the general problem; report wrong tests instead of working around them.
- **Temporary files:** ask for cleanup at the end if you do not want scratch files left.
- **Long tasks across context windows:** keep state in files (tests or status as JSON, progress notes as text, git as the log). Tell the agent how to restart: which files to read first.
- **Context limits:** in a harness that compacts (Claude Code), tell the agent not to stop early because of the token budget and to save state before compaction.

## Sub-agents
- Newer models delegate readily, sometimes where a direct grep would do. Anthropic's suggested guidance, paraphrased: use sub-agents for parallel, isolated or independent workstreams; for simple tasks, sequential steps, single-file edits or work that needs shared context, work directly.
- Each sub-agent prompt is the only context it has. Use the per-agent brief in `brief-and-loop.md`.
- In Workflow scripts, prefer a JSON schema over prose output instructions.

## Research prompts
Give success criteria, ask for verification across sources, and for big questions ask it to keep competing hypotheses with confidence levels in a notes file. In this workspace, running-research-ops sets the rules (question tree, quotes, grades).

## Templates

### Claude Code / `claude -p` task
```
## Objective
[One sentence. Why, if it changes the approach.]
## Context
[Current state, files, what was tried.]
## Target state
[What done looks like. Binary checks.]
## Scope
Work only in: [paths]. Do not touch: [paths].
## Constraints
Only make changes directly requested.
## Acceptance criteria
- [ ] [check with the command that proves it]
## Action boundaries
Proceed with reversible, in-scope edits and checks. Stop and ask before deleting files,
adding dependencies, pushing, sending messages or changing settings.
## Progress evidence
Ground every completion claim in a tool result or command output.
```
For `claude -p` from Task Scheduler: add the allowlist of tools in the command, never bypass permissions, and write results to a file the next session reads.

### Claude in Chrome / browser agent
Describe the outcome, not the clicks. Add: "Research only. Do not buy, submit forms, send messages or accept cookie banners beyond necessary-only. Ask me before any of these." Add a stop rule for logins and CAPTCHAs: stop and tell the user.
