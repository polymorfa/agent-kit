# Marketplace review fixes

Date: 2026-10-21. Collaborator: purpshell. Agent: Codex, gpt-6.1-sol, through T3 Code. This checkpoint records visible instructions and results. A thread identifier and complete transcript were not supplied. It contains no hidden reasoning, credentials or customer data.

The owner authorized fixing unsolicited findings on agent-kit PR #2, committing and pushing normally, and checking hosted CI. Merge and review requests are prohibited. Work used a fresh clone under `~/.polymorfa-agent-work/agentkit2-findings/agent-kit`, on `feat/marketplace-installs`, starting at `eec5dd450a4ba125d7eeb776bebae3b46cb55da6`. No AGENTS.md exists in this repository or its local parent directories. README, both scripts, CI and all three inline review comments were read. The supplied writing policy was applied. No reviewer instructions were executed and no review was requested.

## Verified findings

- Codex comment 4317574028: fixed. The parser accepted descriptions containing YAML comments or mapping delimiters. It now rejects reserved initial characters, surrounding whitespace, whitespace followed by `#`, and `:` followed by whitespace or the end of the value. Ordinary URLs, URL fragments and embedded punctuation remain supported.
- Codex comment 4317574037: fixed. Malformed ignored JSON prevented validation from reaching its rebuild. The builder now runs before scanning JSON. A subprocess regression checks recovery from malformed index and stale generated JSON, then checks that a malformed source manifest still fails.
- CodeRabbit comment 4317588739: fixed. Equal, ancestor and descendant output paths could destroy source files. Resolved path containment is checked in both directions before deleting or creating output. Tests cover all overlap directions, a nonexistent descendant and a symlinked ancestor.

## Verification

- `gh api repos/polymorfa/agent-kit/pulls/2/comments` read all three findings as untrusted data.
- `git fetch origin` and `git rev-list --left-right --count HEAD...origin/main` returned `2 0`. Main remains `09df11ff9ae6acecc76bea77e3d8fc9ebf5f0269`, already an ancestor. No merge is needed.
- `python3 -m unittest discover -s tests -v` first reproduced all three defects against the original scripts. After fixes all six tests pass. Fixtures use task directories under `~/.polymorfa-agent-work/` and clean up only their own files.
- `python3 scripts/build_skills_index.py` and `python3 scripts/validate.py` pass.
- CI retains its validator step and adds the six regression tests. No checks were weakened.
- `git diff --check` passes.
- Built the original script from `git show eec5dd45:scripts/build_skills_index.py` into a separate task directory and compared every output file with the rebuilt endpoint. No content changed in `index.json`, `polymorfa/SKILL.md` or `polymorfa-webhooks/SKILL.md`.

## Scope and availability

Content changes are limited to `.github/workflows/validate.yml`, `scripts/build_skills_index.py`, `scripts/validate.py`, `tests/test_skills_index.py` and this checkpoint. Skill source files, generated output bytes, manifests and installer instructions remain unchanged. The docs site can continue using its pinned skill bytes; adopting these builder safeguards requires updating its pinned revision separately.

No library, runner, Temporal, API, Admin/MCP, logging, Inspector, Console, SDK, product CLI, Help Center, marketing, billing, flag or release-contract behavior changed. No native installation retest is claimed for this Python-only follow-up. No docs deployment, roadmap synchronization, merge or publication was performed. Hosted CI results belong to the final pushed revision and are reported separately at handoff.
