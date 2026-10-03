---
name: polymorfa-webhooks
description: Implement or debug Polymorfa webhook verification, event handling, and delivery retries.
---

# Polymorfa webhooks

Find the webhook guide and exact payload/version reference through the [documentation index](https://docs.polymorfa.com/llms.txt) or documentation MCP. Do not invent signature headers, signing algorithms, event names, or SDK helpers.

Preserve raw request bytes for signature verification. Authenticate before processing an event. Use the project's secret storage and avoid logging payloads or signing material. Keep responses fast and process work through the application's durable queue when it has one. Deduplicate using the documented delivery/event identity rather than message text.

Use local signed fixtures to test a valid signature, a modified body, a missing signature, and a repeated delivery. A local fixture does not prove public reachability or live delivery. Changing remote endpoints or replaying real deliveries requires authorization for those effects.
