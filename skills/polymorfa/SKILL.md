---
name: polymorfa
description: Set up Polymorfa tooling or build a WhatsApp integration with its API, SDK, CLI, or MCP tools.
---

# Polymorfa

Read the [setup instructions](https://docs.polymorfa.com/agent-setup/prompt.md) for installation or agent configuration. For API work, use the documentation MCP to find the exact operation and read its guide before changing code. Without it, use the [agent index](https://docs.polymorfa.com/llms.txt) and page Markdown.

## Choose the connection

- Documentation MCP searches public guides. It cannot inspect customer resources.
- Hosted API MCP uses a Polymorfa credential and invokes the same operations as the API. Read its [authorization guide](https://docs.polymorfa.com/integrations/mcp-server.md).
- CLI local MCP inspects local CLI sessions and event listeners. Read the [CLI guide](https://docs.polymorfa.com/tools/cli-api.md). It is a separate connection.

Use the SDK when it covers the operation; otherwise use the documented API. Do not infer SDK methods from API names. Keep Messaging, Platform, and Graph APIs and their credentials distinct.

## Bound the task

Preserve existing files and agent configuration. Use the project's secret mechanism and the least-privileged credential. Never print credentials or include them in source, logs, URLs, or chat. A missing scope is a blocker, not permission to bypass it.

Follow the user's authorized scope. Ask before sending a message, creating or deleting remote resources, or incurring charges unless that effect was already authorized. Do not send a test message just to prove setup worked. Do not retry a write with an uncertain outcome.

## Verify

Check installation and MCP tool discovery, then perform one permitted read if a credential is available. Report installation, authenticated access, and deployed availability separately. For webhook handlers, use the bundled polymorfa-webhooks skill.
