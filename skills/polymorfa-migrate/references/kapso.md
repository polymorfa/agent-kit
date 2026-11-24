# Kapso reference for polymorfa-migrate

Maps Kapso (https://docs.kapso.ai) to Polymorfa. Checked on 24 November 2026 against Kapso's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user), `not verified` (not checked; read the docs before relying on it).

The human guide is https://docs.polymorfa.com/migrate/kapso.

## Requests and credentials

Kapso: WhatsApp API at `https://api.kapso.ai/meta/whatsapp/v24.0/{phone_number_id}/...`, which mirrors Meta's Graph API shapes. Platform API at `https://api.kapso.ai/platform/v1/...` (customers, setup links, phone numbers, webhooks, broadcasts, conversations, contacts, workflows, functions). One project key in the `X-API-Key` header authenticates all of them; the WhatsApp API also accepts `Authorization: Bearer`. The MCP server is at `https://api.kapso.ai/mcp`. Request bodies carry `messaging_product` and the other Meta fields. A send has no documented idempotency key.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. The phone number ID is part of the path. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`, and Platform API paths with `https://api.polymorfa.com/platform`.

Ask how each Kapso number was connected and who owns each WhatsApp Business Account before planning the move. Kapso offers instant setup (a number Kapso manages), coexistence with the WhatsApp Business app, your own SIM, and manual setup with a Meta app. A Kapso-managed instant-setup number cannot be assumed to move: Kapso's docs do not say it can. A number paired through coexistence connects to one provider at a time. A number registered to Cloud API with another provider keeps that provider's registration PIN; Polymorfa stops before it replaces a PIN it does not hold, so the user resolves it with Kapso first. Templates belong to the WhatsApp Business Account, not the provider. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Kapso capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Connect with Embedded Signup or your own SIM | Connection created through a QuickLink with Meta Embedded Signup | same | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence with the WhatsApp Business app | Same choice in Embedded Signup | same | `connections/cloud-api-setup` |
| Instant setup number (Kapso-managed) | Not offered | gap | none |
| Customers and setup links (`/customers`, `/customers/{id}/setup_links`) | Customers, with a spending limit and pairing links per customer, and QuickLink pages | more | `customers/index`, `customers/pairing-links`, `connections/quicklink` |
| `POST /{phone_number_id}/messages` (text, media, location, contacts, reactions, interactive) | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| Template send and template CRUD | `POST`, `GET`, `DELETE /{waba-id}/message_templates`, and `type: "template"` sends; project templates also have preview | more | `messaging/templates` |
| Mark as read with typing indicator | `status: "read"` on the messages endpoint (Cloud API Connections); typing through the Messaging API | same | `messaging/send` |
| Media upload, get, delete | `POST /{phone-number-id}/media`, `GET /{media-id}`, `DELETE /{media-id}` | same | `messaging/media` |
| Received media download | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Marketing messages | `/{phone-number-id}/marketing_messages`, `/{waba-id}/marketing_messages/status` | same | `api/graph/index` |
| Business profile, block users | `/{phone-number-id}/whatsapp_business_profile`, `/{phone-number-id}/block_users` | same | `connections/business-profile`, `api/graph/index` |
| WhatsApp Flows: create, upload JSON, publish | `/{waba-id}/flows` lists and creates; edit and publish in the Flow builder | different | `messaging/flows` |
| Broadcasts (template to a list, schedule, suppressed opt-outs, per-recipient status) | Campaigns with audiences, opt-outs, pacing and per-recipient status; launch from Pro Connections | more | `campaigns/index`, `campaigns/send`, `campaigns/opt-outs` |
| Stored conversations, contacts and messages (dashboard, retention windows) | Hosted message history, an opt-in beta; no content is kept by default | different | `messaging/history` |
| Shared inbox, embedded inbox (iframe) | Inbox and chat components for the user's own app | different | `ui-kit/inbox` |
| Conversation assignment and handoff | Not offered | gap | none |
| Workflows, agent steps | No workflow builder. The user's code, or an agent over MCP | different | `development/mcp` |
| Functions (JavaScript on Cloudflare Workers) | Functions, in private beta | different | `development/functions` |
| Calling API actions (`pre_accept`, `accept`, `reject`, `terminate`, `connect`) | `POST /{phone-number-id}/calls` takes Meta's call actions unchanged. Set `hostCloudApiCalls` to `true` and Polymorfa Calls answer in the browser, server code or SIP; the Graph `/calls` endpoint then refuses to answer | more | `calls/server` |
| Voice agents over WebRTC (Pipecat, ElevenLabs Agents) | Server code reads and writes the call audio | same | `calls/server` |
| SIP | Not covered by Kapso's guides. SIP trunks carry audio to the user's PBX | more | `calls/sip-trunks` |
| Call logs | Call history with quality stats | same | `calls/records` |
| Call recordings and transcripts | Polymorfa does not record calls | gap | none |
| Phone number health check | BanSafe Health score on production linked-device connections | different | `safety/health` |
| MCP server (47 tools) | Hosted MCP server with 200+ tools, and a local MCP in the CLI | more | `development/mcp` |
| CLI `@kapso/cli`, TypeScript SDK | Polymorfa CLI and SDKs | more | `development/cli` |
| n8n node | n8n, Zapier and Make integrations | more | `integrations/overview` |
| Sandbox number (text and interactive only) | Test connections on a simulated network, at 0 credits | more | `testing/index` |
| Usernames, conversion events, display name requests | Not verified on the Graph API | not verified | `api/graph/index` |

## Webhooks

Kapso sets webhooks per phone number, in two kinds. The `kapso` kind sends events with an `X-Webhook-Event` header; the `meta` kind sends Meta's payload (one per number). Both carry a hex HMAC-SHA256 of the raw body in `X-Webhook-Signature` (no `sha256=` prefix), an `X-Idempotency-Key` for deduplication, and expect `200 OK` within 10 seconds. A failed delivery is retried 10 seconds and 40 seconds after the failures, 3 attempts and about 50 seconds in all. Kapso pauses a webhook when, within 15 minutes, at least 40 deliveries were made, at least 10 failed and at least 85% failed. Message buffering can batch `whatsapp.message.received` events. Project webhooks, set once per project, carry number, account and workflow events and no messages. Call events arrive only on a `meta` kind webhook. The `from` field may be missing; Kapso sends business-scoped user IDs instead.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256` (`sha256=` prefix), or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Kapso | Polymorfa | Status |
| --- | --- | --- |
| `whatsapp.message.received` | `message.received`, or Meta `messages` in the meta format | same |
| `whatsapp.message.sent` | `message.sent` | same |
| `whatsapp.message.delivered`, `whatsapp.message.read` | `message.ack` | same |
| `whatsapp.message.failed` | `message.failed` | same |
| `whatsapp.contact.marketing_preference_changed` | `contact.opted_in`, `contact.opted_out` | different |
| `whatsapp.conversation.created`, `.ended`, `.inactive` | No conversation events. Build from message events | not verified |
| `whatsapp.thread.ownership_changed`, `.standby` | Not verified | not verified |
| `whatsapp.contact.identity_changed` | Not verified | not verified |
| `whatsapp.phone_number.*`, `whatsapp.account.*` (project webhooks) | `connection.status`, `connection.logged_out`, `connection.restriction_updated` | different |
| `workflow.execution.*`, `kapso_agent.run.*`, `project.event` | No equivalent | gap |
| Call events (Meta payload) | `call.received`, `call.accepted`, `call.missed`, `call.ended` | same |

## Differences to agree with the user

- Requests change base URL, header and path: add the Meta phone number ID in the path and replace `X-API-Key` with a bearer token. Bodies stay Meta's.
- Verify the signature on the raw body. Polymorfa's Meta-format signature carries a `sha256=` prefix; Kapso's has none. Drop any code that unwraps Kapso's batch envelope unless Polymorfa batching is confirmed in the webhook docs.
- Add an `Idempotency-Key` header to Messaging API sends. Kapso documents none.
- Kapso customer, setup link, broadcast, workflow and business-scoped user identifiers do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Kapso Workflows and Functions run on Kapso. Agree with the user where that logic runs.
- Download received media when the event arrives. Kapso's docs describe no data export; ask the user what to take out of Kapso before cancelling.
- Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account on both platforms.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Kapso one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Cancel the Kapso plan only after every number runs on Polymorfa.
