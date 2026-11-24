# TimelinesAI reference for polymorfa-migrate

Maps TimelinesAI (https://timelines.ai/docs/llms.txt) to Polymorfa. Checked on 24 November 2026 against TimelinesAI's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/timelinesai.

TimelinesAI is a shared inbox with CRM sync, and its Public API sits on top of the inbox. Polymorfa is an API. Inbox features have no equivalent; section 4 lists them.

## 1. Mapping

Base URL on TimelinesAI: `https://app.timelines.ai/integrations/api`. Polymorfa Messaging API: `https://api.polymorfa.com/messaging/{connection}`; Platform API: `https://api.polymorfa.com/platform`.

### 1.1 Accounts and pairing

| TimelinesAI capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| QR code in the app | Create a QuickLink: `POST /messaging/quicklinks`. The Connection id is returned as `data.connection`. | different | `connections/quicklink` |
| `POST /whatsapp_accounts/phone_pairing` (phone, states `starting`, `awaiting_code`, `connected`, `expired`, `code_unavailable`, `failed`) | QuickLink pairing code, or `POST /messaging/{connection}/pair/code` with `{"phone":"+15550001111"}` (code in `data.code`). Direct pairing needs team access, else `403` pointing to QuickLink. | same | `connections/direct-pairing` |
| `GET /whatsapp_accounts` | `GET /platform/connections` (`status` is `CONNECTING`, `CONNECTED` or `DISCONNECTED`), push via `connection.status` | more | `connections/manage` |
| Disconnect a WhatsApp account | `POST /platform/connections/{connectionId}/logout` (`202`, async); `POST .../stop` pauses without unlinking | same | `connections/manage` |
| WABA account | A Cloud API Connection (Embedded Signup, beta) or Hybrid; the same send call serves both routes | more | `connections/cloud-api-setup` |

### 1.2 Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?}` (see `messaging/send`). Response: Polymorfa `id`, `whatsapp_ids`, `conversation`, `timestamp`, `type`, `content`, `status`.

| TimelinesAI capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /messages` (`phone`, `text`, `whatsapp_account_id`, `label`) | `conversation:{phoneNumber:"+15551234567"}` and `content.text`. The Connection is in the path. | same | `messaging/send` |
| `POST /chats/{chat_id}/messages`, `POST /messages/to_jid`, `POST /messages/to_chat_name` | `conversation` with the Polymorfa conversation id. No JID or chat-name input. | different | `messaging/send`, `messaging/ids` |
| `POST /files` (URL) or `POST /files_upload` (form), then `file_uid` on the send | `content.image`, `content.video`, `content.voice` or `content.file` with `url` or `base64`, in the same call. No separate upload. | same | `messaging/send`, `messaging/media` |
| Send voice message | `content.voice` with `ptt: true` | same | `messaging/send` |
| Reactions (`GET` and `PUT` on a message) | `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| Typing indicator | `POST /messaging/{connection}/messages/typing` with `state: typing`, `recording` or `paused` | same | `messaging/send` |
| Mark a chat as read | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| `GET /messages/{message_uid}` and `/status_history` (queued, sent, delivered, read, failed) | `message.ack` and `message.failed` events; the send response `status` | different | `api-events` |
| Message comments | No equivalent. | gap | none |
| `POST /waba/messages`, `POST /waba/chats/{chat_id}/messages` | The same send call on a Cloud API Connection. Templates use `content.template`. Free-form sends outside the 24-hour customer service window fail with `conversation_window_closed`. | same | `messaging/send`, `messaging/templates` |
| WABA template list and get | Template create, preview and submit under `/messaging/projects/{projectSlug}/templates`; status changes arrive as `template.status`. | more | `messaging/templates` |
| Idempotency (not documented) | `Idempotency-Key` header, 1-hour receipt | more | `development/idempotency` |
| ~2 second delay between API messages | Connection tier throughput (Standard 10 messages a second, Pro 100) and optional Safe Mode pacing and typing | different | `billing/connection-tiers`, `safety/safe-mode` |

### 1.3 Chats, labels, history and groups

| TimelinesAI capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /chats`, `GET /chats/{chat_id}/messages`, search messages | `GET /messaging/{connection}/chats` and `.../chats/{conversation}/messages` through the history API, a beta that needs hosted message storage on the Connection and the team's opt-in. Contains only messages after storage was enabled. | different | `messaging/history` |
| Chat labels: list, add (`PUT`), replace (`POST`) | `GET/POST /messaging/{connection}/labels`, `PUT/DELETE .../labels/{labelId}`, and `GET/PUT .../labels/chats/{conversation}`. `PUT` replaces the full set; read-modify-write to add one. | same | `messaging/linked-device-controls` |
| Group chats (filter, send) | Full group operations under `/messaging/{connection}/groups`: create, members, admins, subject, description, picture, invite codes, settings, join and leave | more | `messaging/contacts-and-groups` |
| Mass messaging with a credit quota | Campaigns and audiences (`/platform/campaigns`, `/platform/audiences`); Pro tier; opt-outs and per-recipient status | more | `campaigns` |
| Add note, assign (`responsible`), close and reopen, rename, delete a chat | Not offered. | gap | none |
| Contacts export, hidden phone numbers, Click-to-WhatsApp attribution (Pro) | Not offered as such. Contacts are `GET /messaging/{connection}/contacts`. | gap | `messaging/contacts-and-groups` |
| ChatGPT auto-response, Workflow Builder, CRM integrations, Zapier and Make | Not offered. Use the API, webhooks and the MCP server. | gap | `development/mcp` |

### 1.4 Calls

| TimelinesAI capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Call list, get, recording, transcript | Call records and statistics. Polymorfa does not record calls; a call's audio is available to your code on a server or browser call. | different | `calls/records`, `calls/server` |
| Call missed, ended webhooks | `call.missed`, `call.ended`, plus `call.received`, `call.accepted`, `call.rejected` and more | more | `api-events` |
| (calls are not placed through the Public API) | Place and answer calls in a browser, from server code, or over a SIP trunk | more | `calls` |

### 1.5 MCP

| TimelinesAI | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| WhatsApp MCP (list chats, read history, send replies, set labels, assign teammates, check quotas) | Hosted MCP server with 150+ tools, and a local MCP server in the CLI | more | `development/mcp` |

### 1.6 Partner API (multi-tenant)

| TimelinesAI capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Create and update a workspace (seat allocation 1 to 99), create users | Customers API: `POST /platform/customers`, archive and restore, a per-Customer monthly cap. No seats. | different | `customers` |
| Generate a QR link for a user, embedded with `postMessage` | Customer pairing links: `POST /platform/customers/{customerId}/pairing-links`, the hosted QuickLink page with your brand. No embeddable script. | different | `customers/pairing-links`, `connections/quicklink` |
| Get and rotate the workspace Public API token | API keys and project tokens, created in the Console with scopes, expiry and revocation | different | `development/api-keys` |
| Partner webhooks (seats full, quota full, account connected or disconnected, token rotated) | `customer.connection.attached`, `customer.connection.disconnected`, `customer.pairing_link.connected` and related `customer.*` events | different | `api-events` |

## 2. Auth and identifiers

| TimelinesAI | Polymorfa |
| --- | --- |
| `Authorization: Bearer <Public API token>`, one token per workspace, scopes by resource | `Authorization: Bearer <credential>`. Team key `pmfa_`, project token `pmfa_pt_`, client token `pmfa_ct_`. Scopes per method (`messages:write`, `connections:manage`, `webhooks:manage` and others), expiry, rotation and revocation. |
| Partner API: JWT signed with the Partner Secret (HS256), `X-TL-Partner-Id` | Team key plus the Customers API |
| `whatsapp_account_id` such as `14155551234@s.whatsapp.net` | Connection id in the path: an opaque decimal string, not a secret. List with `GET /platform/connections`. |
| `chat_id`, `message_uid`, `file_uid` | Polymorfa `conversation.id` and message `id` (opaque decimal strings, scoped to the Connection). Nothing converts: list again after pairing and store the new ids. WhatsApp's own id is in `whatsapp_ids`. |
| Phone `+14155551234` or `14155551234` | `conversation.phoneNumber` in E.164 with `+`. The returned `phoneNumber` is WhatsApp's resolved phone; match conversations by `conversation.id`. |
| JID for groups and technical integrations | No JID input. Group `id` is an opaque decimal string; build a map with `GET /messaging/{connection}/groups`. |

A migration agent cannot mint keys. Ask the human to create a project token with the scopes the integration needs, then set `POLYMORFA_KEY`.

## 3. Webhook migration

### 3.1 Transport

| Topic | TimelinesAI | Polymorfa |
| --- | --- | --- |
| Registration | `POST /webhooks` per event type (URL, enabled flag); list, get, update, delete | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` default or `meta`), `retryPolicy`, `enabled`. Needs `webhooks:manage`. Each mutation needs an `Idempotency-Key`. |
| Signature and headers | None. "Authentication of the request or customizing headers is not supported." | `native`: `X-Webhook-Signature: <lowercase hex>`. `meta`: `X-Hub-Signature-256: sha256=<hex>`. Both HMAC-SHA256 over the exact raw body with the endpoint's signing secret, constant-time compare. |
| Retries | 2 more attempts after a non-2xx or timeout (3 in total), schedule not stated; the owner is emailed after several failures; not auto-disabled | Up to 8 attempts over 24 hours; fixed offsets 30 s, 2 min, 10 min, 1 h, 4 h, 12 h, 24 h. Retries on network error, timeout, `408`, `429`, `5xx`. |
| Response window | 2xx within 5 seconds | 2xx within 30 seconds per attempt. Save durably, process later. |
| Duplicates | "May be delivered more than once"; dedupe on `message_uid` | At least once, unordered. The envelope `id` is stable across retries; dedupe on it. |
| Redelivery | none | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |

### 3.2 Envelope

TimelinesAI: top-level `event_type`, `chat`, `whatsapp_account`, `message` (`text`, `direction`, `origin`, `timestamp`, `message_uid`, `reply_to_uid`, `sender`, `recipient`, `attachments`). Attachment URLs are pre-signed and expire after 15 minutes.

Polymorfa:

```json
{
  "id": "<event id>",
  "connection": "739182640518203",
  "timestamp": "2026-11-24T10:05:00.000Z",
  "event": "message.received",
  "payload": { }
}
```

`whatsapp_account` becomes `connection`, `event_type` becomes `event`, and message fields move under `payload`.

### 3.3 Events

| TimelinesAI `event_type` | Polymorfa event | Status |
| --- | --- | --- |
| `message:received:new`, `message:new` (incoming) | `message.received` | same |
| `message:sent:new` | `message.sent` (and `message.echo` for sends from the phone) | same |
| `message:delivered`, `message:read` | `message.ack` | same |
| `message:edited`, `message:deleted` | `message.edited`, `message.revoked` | same |
| `message:reaction` | `message.reaction` | same |
| `chat:new`, `chat:incoming:new`, `chat:outgoing:new`, `chat:renamed` | No chat-created or renamed event. The first message arrives as `message.received` or `message.sent`. | gap |
| `chat:responsible:assigned`, `chat:responsible:unassigned` | None (no assignment). | gap |
| `call:incoming:missed`, `call:incoming:ended`, `call:outgoing:ended` | `call.missed`, `call.ended` | same |
| `call:recording:ready`, `call:transcript:ready` | None (no recordings). | gap |
| Account reconnected, disconnected | `connection.status`, `connection.connected`, `connection.logged_out` | same |
| `whatsapp:account:reachout_timelock:active` and `:cleared` | `connection.restriction_updated` (`type: reachout_timelock`, `active`) | same |
| WABA template approved, rejected, disabled | `template.status` | same |

### 3.4 What a migrating handler must change

1. Verify `X-Webhook-Signature` on the raw bytes first. This is new; TimelinesAI sent no signature.
2. Read `event`, not `event_type`; read the body under `payload`.
3. Key people and chats by `conversation.id`.
4. Respond 2xx after a durable save, dedupe on the envelope `id`, accept reordering.
5. Subscribe to specific `eventTypes`.
6. Download media when the event arrives, or save it with `POST /messaging/media/{id}/download-and-save`.

## 4. Gaps and behaviour differences a migrating agent must handle

Gaps (not offered):

1. Inbox features: chat assignment, internal notes, close and reopen, message comments, rename and delete chat, the Workflow Builder, CRM integrations and ChatGPT auto-response.
2. Call recordings and transcripts.
3. Contacts export and Click-to-WhatsApp ad attribution.

Behaviour differences:

- **No queue on disconnect.** A send to a disconnected Connection is refused: `503 connection_not_ready` (sync) or `message.failed`. Keep an outbox and retry with the same `Idempotency-Key` (1-hour window) when the Connection reports `CONNECTED`.
- **First messages to people who never wrote.** TimelinesAI sends to any phone number. Outside Campaigns, Polymorfa refuses a first message to such a contact (`bansafe_cold_blocked`, `403`). Route outreach through Campaigns (Pro) or message people who wrote first.
- **Pacing.** The fixed ~2 second delay is gone. Polymorfa enforces warm-up and throttles (`bansafe_daily_allowance_reached`, `bansafe_throttled`, both `429` with `Retry-After`) and WhatsApp's new-chat cap (`new_chat_limit_reached`). Respect `Retry-After`. Safe Mode (`pacing`, `typing`, `presence`, `reads`) is off by default and needs Standard or Pro.
- **Media.** Polymorfa keeps no attachment files. Download a received file from its message, or save it to your own storage with `POST /messaging/media/{id}/download-and-save`.
- **Ids.** Everything is an opaque decimal string. Do not parse or cast it.
- **History.** There is no list of everything the phone has. History needs hosted message storage (beta) and is bounded by retention.
- **Cloud API Connections differ.** Edits, deletes, groups and channels are linked-device only; free-form sends outside the 24-hour service window fail with `conversation_window_closed`; templates only; the typing indicator needs an inbound message.
- **Async completion.** Connect, start, stop, restart and logout return `202` with an `operationId`. Wait on `connection.status` or `GET /platform/operations/{id}`.
- **Pairing.** Pairing is human-in-the-loop: the phone owner scans a QR code or enters a code.
- **Billing.** Polymorfa bills each Connection per online day by tier (Free, Standard, Pro). There are no seats and no API call allowance. Meta's template fees apply on both platforms.
- **Test mode.** A test Connection sends only to other active test Connections in the same project. Do not migration-test against real recipients there.
