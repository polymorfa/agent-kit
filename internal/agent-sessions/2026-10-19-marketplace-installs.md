# Marketplace install implementation

Date: 2026-10-19. Collaborator: purpshell. Agent: Codex, gpt-6.1-sol, through T3 Code. The thread identifier was not supplied to this session. This is a sanitized checkpoint of visible task instructions and tool results, not a complete transcript. No hidden reasoning, credentials, or customer data is included.

## Scope and source revision

The owner requested Claude and Codex repository marketplace installs, a Stripe-compatible docs skills endpoint builder, validator coverage, README instructions, and a PR against main. No merge, publication, workflow enablement, or automated review request is authorized. The fresh clone started from main at `09df11ff9ae6acecc76bea77e3d8fc9ebf5f0269`. No contribution guide or AGENTS.md exists in this repository. Work stayed in `~/.polymorfa-agent-work/agent-kit-marketplace/` on `feat/marketplace-installs`.

The OpenAI Docs skill was loaded for official source research. The originating monorepo's writing and checkout preservation rules were supplied by the user. No implementation delegation or automated reviewer was used. Roadmap records were not supplied or reconciled; this checkpoint does not claim Linear or Notion synchronization.

## Schema evidence

- [Anthropic marketplace guide](https://code.claude.com/docs/en/plugin-marketplaces): `.claude-plugin/marketplace.json` requires a name, owner, and plugin entries with name and source. Relative sources resolve from the marketplace root. The entry here uses `./`.
- [OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins): `.agents/plugins/marketplace.json` declares the catalog; `source.path` resolves from its repository root. Root `plugin.json`, `mcp.json`, and `skills/` are supported portable components. No Codex overlay is needed. The guide documents `codex plugin marketplace add owner/repo` and Git ref selection.
- [OpenAI plugin surfaces](https://learn.chatgpt.com/docs/plugins): Codex CLI supports marketplace plugins and requires a new session after installation. The IDE extension does not support plugins.
- Installed `codex-cli 0.163.0`: `codex --help` lists `plugin`; `codex plugin marketplace add --help` accepts local paths, owner/repo with optional ref, HTTPS and SSH Git URLs; `codex plugin add --help` accepts `PLUGIN@MARKETPLACE`.
- [Stripe's live index](https://docs.stripe.com/.well-known/skills/index.json) was fetched. Its shape is `{"skills":[{"name":"...","description":"...","files":["SKILL.md","references/..."]}]}`. Fetching [a listed skill](https://docs.stripe.com/.well-known/skills/stripe-best-practices/SKILL.md) returned Markdown frontmatter, confirming the relative file layout. Stripe content was not copied into this repository.
- [Cursor plugin guide](https://cursor.com/docs/plugins): native marketplace install uses Customize and an Install action. Marketplace listing requires separate publication. This PR does not submit a listing.

## Verification

All installation writes used task-specific directories outside the user's real agent configuration. The local source is the fresh clone, including this patch.

- `python3 scripts/validate.py`: passed. Rebuilds and validates the skills endpoint alongside existing plugin/MCP checks and the two catalogs.
- Claude Code `2.1.303`, with `CLAUDE_CONFIG_DIR` set to the absolute task `claude-config` directory:
  - `claude plugin validate .`: passed without warnings.
  - `claude plugin validate .claude-plugin/plugin.json`: passed.
  - `claude plugin marketplace add <absolute-checkout>`: added `polymorfa`.
  - `claude plugin install polymorfa@polymorfa`: installed version 0.1.0.
  - `claude plugin details polymorfa`: reported two skills (`polymorfa`, `polymorfa-webhooks`) and one MCP server (`polymorfa-docs`). This is component inventory, not a live MCP search.
- Codex CLI `0.163.0`, with `CODEX_HOME` set to the absolute task `codex-config` directory:
  - `codex plugin marketplace add <absolute-checkout> --json`: added `polymorfa`.
  - `codex plugin add polymorfa@polymorfa --json`: installed 0.1.0 into the isolated plugin cache.
  - `codex plugin list --json`: reported the plugin installed and enabled.
- `skills` npm CLI `1.7.2`: `npx --yes skills --help` confirms project install is the default, `--agent` selects the target, `--copy` avoids symlinks, and `--yes` skips prompts. No `--global` option was used.
  - Copied `dist/well-known-skills/` to a task server root at `.well-known/skills/`.
  - `python3 -m http.server 18743 --bind 127.0.0.1 --directory <task-site-root>` served it.
  - From a throwaway task project, `npx --yes skills add http://localhost:18743 --agent codex --skill '*' --yes --copy` found and installed both skills under that project's `.agents/skills/`.
  - Both installed SKILL.md files matched repository source bytes.
- Separate builder fixtures under the task directory: nested `references/guide.md` was included and copied; rebuilding removed a stale output file; validation rejected corrupted bytes; building rejected a source symlink.
- `git diff --check`: passed.

## Availability and handoff

Generated `dist/well-known-skills/` is ignored. The docs build must run the script at a pinned agent-kit revision and copy the generated contents to `public/.well-known/skills/` or an equivalent static root. No docs deployment was performed. The domain install command remains gated on that deployment. Default-branch repository marketplace installs remain gated on merging this PR.

Gemini and Cursor executables were absent. Their native installs were not tested. The existing extension/plugin files and all skill contents remain unchanged. API, SDK, CLI product behavior, Admin, authentication, billing, and customer data are unaffected by these packaging changes. No workflow files were changed or re-enabled.

A useful optional engineering article would compare manifest validation with real isolated installs, using the Claude component inventory and HTTP skill-byte checks as evidence. It would keep unmerged and undeployed availability explicit.

## Remote install checkpoint

At pushed implementation revision `0bd7c800185c5c63d241dab3d001d5fb3fe1e369`, both Git-backed installs also passed in separate task configurations:

```sh
CLAUDE_CONFIG_DIR=<task>/claude-git-config claude plugin marketplace add 'https://github.com/polymorfa/agent-kit.git#feat/marketplace-installs'
CLAUDE_CONFIG_DIR=<task>/claude-git-config claude plugin install polymorfa@polymorfa
CLAUDE_CONFIG_DIR=<task>/claude-git-config claude plugin details polymorfa
CODEX_HOME=<task>/codex-git-config codex plugin marketplace add polymorfa/agent-kit --ref feat/marketplace-installs --json
CODEX_HOME=<task>/codex-git-config codex plugin add polymorfa@polymorfa --json
```

Claude cloned the selected branch and reported two skills and the documentation MCP server. Codex fetched the branch, installed version 0.1.0, and its cache contained the root portable manifest, MCP configuration, and both skill files. Remote and local branch heads matched that SHA.

The skills-only Git path also passed from a second throwaway project: `npx --yes skills add https://github.com/polymorfa/agent-kit --agent cursor --skill '*' --yes --copy` installed both skills. This checks the skills installer with Cursor selected, not the native Cursor runtime.
