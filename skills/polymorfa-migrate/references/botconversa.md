# BotConversa reference for polymorfa-migrate

Maps the BotConversa API (https://ajuda.botconversa.com.br/integracoes/api-botconversa/documentacao-api-botconversa) and its app features to Polymorfa. Checked on 24 November 2026 against BotConversa's public help center and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/botconversa.

## What BotConversa is

BotConversa is a WhatsApp app: a flow builder, GPT assistants, a team inbox, a Kanban board and broadcasts. Its REST API is a small control surface over that app. The API cannot read messages or conversation history, cannot create or edit flows, cannot manage message templates and exposes no reports. Most of what a customer built lives in the app, not in code, so the agent must ask the human which flows and automations matter before it changes anything.

## 1. Mapping

Base URL: `https://backend.botconversa.com.br/api/v1/webhook`. Paths are relative to it and end in a slash. Auth is an `API-KEY` header. The key belongs to one company. A company connects one number.

### 1.1 Connection

| BotConversa capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Configurações, Conexão, Conectar meu WhatsApp: QR code (Starter) | QuickLink: `POST /messaging/quicklinks`. The Connection exists when the link is created; its ID is returned as `data.connection`. Direct pairing: `GET /messaging/{connection}/pair/qr`, `POST /messaging/{connection}/pair/code` (needs direct-pairing access) | different | `connections/quicklink`, `connections/direct-pairing` |
| Official API connection (Pro) | Meta Cloud API Connection through Embedded Signup inside a QuickLink. Needs access for the team | different | `connections/cloud-api-setup` |
| Coexistence (Pro) | The same setup, with the choice to keep using the WhatsApp Business app | same | `connections/cloud-api-setup` |
| A second number needs a second company | Another Connection in the same project. Group them by business with the Customers API | more | `customers` |
| Restart, disconnect | `POST /platform/connections/{connectionId}/restart`, `POST /platform/connections/{connectionId}/logout`. Both return `202` with an operation id | same | `connections/manage` |

### 1.2 Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?}`. See `messaging/send`.

| BotConversa capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /subscriber/{id}/send_message/` with `type` `text` | `content.text`, with `conversation.phoneNumber` | same | `messaging/send` |
| `send_message` with `type` `file` | `content.image`, `content.video`, `content.voice` or `content.file` (`url` or `base64`) | more | `messaging/send` |
| `POST /subscriber/{id}/send_flow/` | No flow builder. Rebuild the flow as code, or as a WhatsApp Flow form for a form step | different | `messaging/flows` |
| Message templates, created in the app on the official route | `POST /messaging/projects/{projectSlug}/templates`, preview, submit for approval. Only Cloud API Connections need Meta's approval | more | `messaging/templates` |
| Free text outside the 24-hour window on the official route (the API answers success and delivers nothing) | A Cloud API send outside the window fails with `conversation_window_closed`. Read the window with `GET /messaging/{connection}/chats/{conversation}/service-window`. Send a template instead | more | `messaging/send` |
| Typing delay and broadcast delay | Safe Mode pacing and typing (Standard and Pro), off until turned on | different | `safety/safe-mode` |

### 1.3 Contacts, tags and fields

| BotConversa capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /subscribers/`, `POST /subscriber/`, `DELETE /subscriber/{id}/delete/` | No contact record to create. Send to a phone number, and keep customer records in the customer's own database. Read a Connection's contacts with `GET /messaging/{connection}/contacts` | different | `messaging/contacts-and-groups` |
| `GET /subscriber/get_by_phone/{phone}/` | `GET /messaging/{connection}/contacts/check?phone=` returns `exists`, `id` and `phoneNumber` | different | `messaging/user-identities` |
| `GET /tags/`, `POST` and `DELETE /subscriber/{id}/tags/{tag_id}/` | Labels: `GET` and `POST /messaging/{connection}/labels`, `PUT` and `DELETE /messaging/{connection}/labels/{labelId}`, `GET` and `PUT /messaging/{connection}/labels/chats/{conversation}`. Linked-device Connections | same | `messaging/contacts-and-groups` |
| `GET /custom_fields/`, `/bot_fields/` and their `POST` and `DELETE` | Not offered as a stored field set. Keep fields in the customer's database. Per-recipient variables exist inside an audience | different | `campaigns/audiences` |
| `POST /subscriber/{id}/change_conversation_status/` | Not offered. Conversation assignment and status belong to the customer's own app | gap | none |

### 1.4 Campaigns and sequences

| BotConversa capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /campaigns/`, `POST /campaigns/create/`, `GET` and `DELETE /campaigns/{id}/` | Campaigns: `GET` and `POST /messaging/projects/{projectSlug}/campaigns`, `GET` and `PATCH .../campaigns/{id}`. Send from Pro Connections. Audiences are team-level, and the opt-out list is enforced at launch and at send time | more | `campaigns`, `campaigns/send`, `campaigns/audiences`, `campaigns/opt-outs` |
| `POST` and `DELETE /subscriber/{id}/campaigns/{campaign_id}/` (add or remove a person) | Audience members, managed through the audience routes | different | `campaigns/audiences` |
| `GET /sequences/`, `POST` and `DELETE /subscriber/{id}/sequences/{sequence_id}/` | Drip sequences: up to 10 steps over days, contacts leave on reply or opt-out. Requires access | different | `campaigns/drip-sequences` |
| Branching replies in a flow | Campaign reply flows: a short fixed tree started by a campaign reply. Requires access | different | `campaigns/reply-flows` |

### 1.5 Team

| BotConversa capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET`, `POST`, `PATCH` and `DELETE /managers/` | Team members and roles (owner, admin, member) in the Console. Invitations assign admin or member | different | `teams/members` |
| Departments, permissions, assignment of conversations | Not offered. Build assignment in the customer's own app, with the UI Kit inbox components if a ready inbox helps | gap | `ui-kit/inbox` |

### 1.6 Events and flows

| BotConversa capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Incoming webhook (Automação, Webhooks): another tool calls BotConversa to create or update a contact | The customer's system calls the REST API directly. Team request quota returns `429` with `Retry-After` | different | `api/rate-limits` |
| Integration block: an HTTP call from inside a flow to the customer's server. One call per block, no error path, 10-second wait for the response mapping | A signed webhook for the events picked, up to 8 attempts over 24 hours, delivery log and replay | more | `development/webhooks` |
| Reading a message through the API | Not possible on BotConversa. On Polymorfa every inbound message is `message.received` | more | `messaging/receive` |
| GPT assistant, AI skills and MCP tools inside the app | The customer's own agent over the hosted MCP server (200+ tools) | different | `development/mcp` |
| Kanban board, built-in CRM | Not offered | gap | none |

## 2. Auth and identifiers

| BotConversa | Polymorfa | Notes |
| --- | --- | --- |
| `API-KEY` header, one key per company, full access to the company. Pressing Atualizar makes a new key and invalidates the old one | `Authorization: Bearer <credential>`. Team key `pmfa_`, project token `pmfa_pt_`, client token `pmfa_ct_` | A migrating agent cannot mint keys. Ask the human to create a project token with the scopes the integration needs (`messages:write`, `connections:manage`, `webhooks:manage` and the read scopes each reference page lists), then set `POLYMORFA_KEY` |
| `subscriber_id`, from `GET /subscriber/get_by_phone/{phone}/` | Phone number in `conversation.phoneNumber`; the response's conversation `id` and message `id` | A subscriber id does not convert. Look people up again |
| Phone number in `phone`: the docs do not state the format; webhooks need the country code | `conversation.phoneNumber` is E.164 with `+`, for example `+5511999990000` | Match conversations by `conversation.id` per Connection, not by the entered string |
| Tag, custom field, flow, sequence and campaign ids | No equivalent ids. Labels have their own ids; campaigns have their own | Remap by name |
| Connection | Connection ID (opaque decimal string in the URL path, not a secret) | Created by QuickLink |

## 3. Webhook migration

BotConversa delivers nothing to the customer's server by itself. The only outbound path is the Integration block (Pro plan) inside a flow, which sends the JSON the flow defines. No signature, retry or event list is documented.

Polymorfa transport:

| Topic | Polymorfa |
| --- | --- |
| Registration | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` default or `meta`). Needs `webhooks:manage`; each mutation takes an `Idempotency-Key` |
| Signature | `native`: header `X-Webhook-Signature`, lowercase hex HMAC-SHA256 over the exact raw body with the endpoint's signing secret. Compare in constant time |
| Retries | Up to 8 attempts over 24 hours. Retries on network error, timeout, `408`, `429` and `5xx` |
| Timeout | 30 s per attempt. Respond fast, process later |
| Idempotency | The event `id` is stable across retries. Dedupe on it. Delivery is at least once and unordered |

Envelope:

```json
{
  "id": "<event id>",
  "connection": "739182640518203",
  "timestamp": "2026-10-19T10:05:00.000Z",
  "event": "message.received",
  "payload": {}
}
```

Events to subscribe to after the move, by what the customer needs:

| Need | Polymorfa event |
| --- | --- |
| A message from a contact | `message.received` |
| Delivery and read state of a send | `message.ack` (`delivered`, `read`, `played`) |
| A failed send | `message.failed`, or a synchronous error with a stable `error.code` |
| Connection lost | `connection.status` (`DISCONNECTED`), `connection.logged_out` |

A migrating handler must: verify `X-Webhook-Signature` on raw bytes first; read `event`, not a flow variable; key people by `conversation.id`; respond 2xx within 30 s after saving; and subscribe to specific `eventTypes`.

## 4. Gaps and behaviour differences a migrating agent must handle

Gaps (not offered):

1. Flow builder, GPT assistant builder, Kanban board and built-in CRM. The agent rebuilds the logic as code with the human, or leaves it on BotConversa.
2. Conversation assignment, departments and conversation status.
3. A stored custom-field set on a contact.

Behaviour differences:

- **Flows are not readable.** The BotConversa API cannot read or export flows. Ask the human to describe or export each flow, and agree which to rebuild as code, which as campaigns or reply flows (access required), and which to leave.
- **No queue on disconnect.** Polymorfa refuses a send to a disconnected Connection with `503 connection_not_ready` or a `message.failed` event. Keep an outbox, and retry with the same `Idempotency-Key` (1-hour window).
- **First messages to people who never wrote.** Outside Campaigns, a first message to such a contact is refused. Route outreach through Campaigns (Pro) or message people who wrote first.
- **Pacing is enforced.** Warm-up allowance, throttle and the WhatsApp new-chat cap return `429`. Respect `Retry-After`.
- **24-hour window.** BotConversa answers success to a free-text send outside the window and delivers nothing. Polymorfa's Cloud API Connections fail with `conversation_window_closed`; send a template.
- **One integration per official-API number.** BotConversa allows one integration on such a number, so it cannot run on both platforms at once. A QR-connected number can, while the phone has a free linked-device slot.
- **Media.** Polymorfa keeps no attachment files. Download a file from its message, or save it to the customer's storage with `POST /messaging/media/{id}/download-and-save`.
- **Cloud API Connections differ.** Edits, deletes, groups and channels are linked-device only, and free-form sends outside the 24-hour window need a template.
- **Billing.** Polymorfa bills per online Connection-day, not per company per month. Meta's per-message charges on Cloud API Connections apply on both platforms.
- **Test mode.** A test Connection sends only to other active test Connections in the same project. Do not run migration tests against real recipients there.
