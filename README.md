# Polymorfa agent kit

Skills and plugin manifests for coding agents integrating Polymorfa. MIT licensed. The bundled MCP searches public documentation; it includes no credentials.

## Install

- Claude Code: clone this repository and run `claude --plugin-dir /absolute/path/to/agent-kit`.
- Gemini CLI: run `gemini extensions install https://github.com/polymorfa/agent-kit`.
- Agent Plugins clients: load the repository root containing `plugin.json` through the client's plugin installer.
- Other skill clients: install the folders under `skills/` through the client's skill installer. Preserve unrelated skills and configuration.

Cursor packaging lives in `.cursor-plugin/`. Marketplace publication and native client acceptance are separate from manifest validation.

Read [agent setup](https://docs.polymorfa.com/agent-setup/prompt.md) to add the CLI or authenticated API MCP. Existing API credentials remain the supported authentication method; do not configure an unimplemented OAuth login.

## Validate

Run `python3 scripts/validate.py`, then check plugin loading and documentation search in your agent.
