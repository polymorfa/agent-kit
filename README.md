# Polymorfa agent kit

Skills and plugin manifests for coding agents integrating Polymorfa. MIT licensed. The bundled MCP searches public documentation; it includes no credentials.

## Install

### Claude Code

After the marketplace change reaches `main`:

```sh
claude plugin marketplace add polymorfa/agent-kit
claude plugin install polymorfa@polymorfa
```

For a local checkout, replace `polymorfa/agent-kit` with its absolute path. To load without installing, run `claude --plugin-dir /absolute/path/to/agent-kit`.

### Codex CLI

Codex supports Git marketplaces. With a CLI version that includes `codex plugin`:

```sh
codex plugin marketplace add polymorfa/agent-kit
codex plugin add polymorfa@polymorfa
```

Start a new session to use the skills and MCP tools. The catalog is `.agents/plugins/marketplace.json`; the existing root `plugin.json`, `mcp.json`, and `skills/` provide the portable plugin. A separate `.codex-plugin/plugin.json` is unnecessary. This uses Polymorfa's repository marketplace, with no OpenAI-curated listing implied. The IDE extension does not support plugins; use the skills-only route below there.

These commands require the catalog on `main`. Local verification used Codex CLI 0.163.0. See OpenAI's [plugin packaging and marketplace guide](https://developers.openai.com/plugins/build/plugins) and [supported plugin surfaces](https://learn.chatgpt.com/docs/plugins).

### Gemini CLI

```sh
gemini extensions install https://github.com/polymorfa/agent-kit
```

The extension uses `gemini-extension.json` and `GEMINI.md`. Native Gemini acceptance has not been run here.

### Cursor

Cursor packaging lives in `.cursor-plugin/`. For a published plugin, open Customize, find the plugin, and select Install with project or user scope, as described in [Cursor's plugin guide](https://cursor.com/docs/plugins). Marketplace publication is a separate step; this repository does not establish a published Cursor listing. Until a listing is available, install the skills into your project:

```sh
npx skills add https://github.com/polymorfa/agent-kit --agent cursor
```

This installs skills only. It does not configure the bundled documentation MCP. Native Cursor plugin acceptance has not been run here.

### Skills only

From the target project directory:

```sh
npx skills add https://github.com/polymorfa/agent-kit
```

Choose the target agent and skills when prompted. Project installation is the default; `--global` changes user configuration. Preserve unrelated skills and configuration. Other skill clients can copy the folders under `skills/` through their skill installer.

Once the docs site serves the generated endpoint, this command will also work:

```sh
npx skills add https://docs.polymorfa.com
```

The domain command requires docs deployment. Generating files in this repository does not publish them.

Read [agent setup](https://docs.polymorfa.com/agent-setup/prompt.md) to add the CLI or authenticated API MCP. Existing API credentials remain the supported authentication method; do not configure an unimplemented OAuth login.

## Build the docs skills endpoint

```sh
python3 scripts/build_skills_index.py
```

The builder writes `dist/well-known-skills/index.json` and `<skill-name>/<file>` for every file in each `skills/<skill-name>/` folder, including nested references. The index format matches [Stripe's live skills index](https://docs.stripe.com/.well-known/skills/index.json):

```json
{
  "skills": [
    {
      "name": "polymorfa",
      "description": "Set up Polymorfa tooling or build a WhatsApp integration with its API, SDK, CLI, or MCP tools.",
      "files": ["SKILL.md"]
    }
  ]
}
```

The real index includes both bundled skills. Files are fetched relative to `/.well-known/skills/<name>/`, for example `/.well-known/skills/polymorfa/SKILL.md`.

Generated output is ignored by Git. The docs build should use a pinned agent-kit revision, run the builder, and copy the contents of `dist/well-known-skills/` to the site's `public/.well-known/skills/` directory (or equivalent static root). Serve the index as JSON and the skill files as their original bytes without authentication or HTML fallbacks. This keeps `skills/` as the source and avoids stale committed copies. Docs integration and deployment are outside this repository change.

The builder supports this repository's plain, single-line `name` and `description` frontmatter. It rejects unsupported metadata and symlinks rather than publishing an ambiguous index.

## Validate

```sh
python3 scripts/validate.py
claude plugin validate .
```

The Python validator checks the plugin manifests, both marketplaces, and the rebuilt endpoint's metadata, complete file inventory, and byte equality. For an isolated Claude check, set `CLAUDE_CONFIG_DIR` to a throwaway absolute directory. For Codex use an isolated `CODEX_HOME`.

To test the HTTP endpoint locally, copy the generated directory to a test server root at `.well-known/skills/`, serve that root, and run this from a throwaway project directory:

```sh
npx skills add http://localhost:18743 --agent codex --skill '*' --yes --copy
```

Omit `--global` so the install stays in that project. Verify the installed skill files against their sources. Plugin installation, MCP discovery, authenticated API access, and deployed availability are separate checks.
