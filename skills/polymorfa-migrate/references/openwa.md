# OpenWA reference for polymorfa-migrate

Maps OpenWA (https://github.com/rmyndharis/OpenWA, docs at https://docs.open-wa.org) to Polymorfa. Checked on 24 November 2026 against OpenWA's published documentation (v0.32.0) and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/openwa.

OpenWA is MIT software that the user hosts. Its calls go to `https://<their host>/api/sessions/{sessionId}/...` with an `X-API-Key` header, and it drives WhatsApp through whatsapp-web.js or Baileys (`ENGINE_TYPE`). Polymorfa native paths start with `https://api.polymorfa.com/messaging/{connection}` and Platform paths with `https://api.polymorfa.com/platform`. Users, groups and messages are addressed by opaque decimal ids, never by WhatsApp ids.

## 1. Mapping

### 1.1 Sessions and pairing

| OpenWA capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /api/sessions` (create) | Create a QuickLink: `POST /messaging/quicklinks`. The Connection exists once the link is created and its id is returned as `data.connection`. Console: Connections > New connection. | different | `connections/quicklink` |
| `POST .../start`, `GET .../qr` | `GET /messaging/{connection}/pair/qr`: JSON `data.qr`, or `?format=image` for a PNG. Needs direct-pairing access for the team, else `403` pointing to QuickLink. | different | `connections/direct-pairing` |
| Pairing code | `POST /messaging/{connection}/pair/code` with `{"phone":"+15550001111"}`; the code is in `data.code`. Same access gate. QuickLink also shows a pairing code. | same | `connections/direct-pairing`, `connections/quicklink` |
| Session status | `GET /platform/connections/{connectionId}`: `status` is `CONNECTING`, `CONNECTED` or `DISCONNECTED`, with `statusReason`. Push events: `connection.status`, `connection.connected`, `connection.logged_out` (`reason`: `banned`, `device_removed`, `unknown`), `connection.restriction_updated`. | more | `connections/manage` |
| Stop, restart, logout, delete a session | `POST /platform/connections/{connectionId}/stop`, `/restart`, `/logout` (`202` with an `operationId`), `DELETE /platform/connections/{connectionId}`. | same | `connections/manage` |
| Many sessions for one operator | Customers API: `POST /platform/customers`, `GET /platform/customers/{id}/connections`, pairing links `POST /platform/customers/{customerId}/pairing-links`, a shared monthly cap per customer. | more | `customers`, `customers/pairing-links` |
| Per-session proxy | Not offered. | gap | none |
| Stored session (whatsapp-web.js LocalAuth, Baileys multi-file auth directory) | Not importable. Connection import accepts a Baileys `SignalStoreSnapshot` or a whatsmeow device store only. Pair the number again with QuickLink. | gap | `connections/import-connections` |
| Profile name, about text and picture | `PUT /messaging/{connection}/profile/name`, `.../profile/status`, `.../profile/picture` (and `DELETE`). | same | `messaging/contacts-and-groups` |

### 1.2 Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?, isForwarded?}`. The response has `id`, `whatsapp_ids`, `conversation`, `timestamp`, `type`, `content` and `status`. Graph equivalent: `POST /graph/whatsapp/{version}/{phoneNumberId}/messages` (Meta request shape).

| OpenWA capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `send-text` (`chatId`, `text`) | `content.text`. `conversation.phoneNumber` is E.164 with `+`. | same | `messaging/send` |
| `send-image`, `send-video`, `send-audio`, `send-document` | `content.image`, `content.video`, `content.voice` (`ptt:true` for a voice note), `content.file` (`url` or `base64`, `caption`, `filename`, `mimeType`). Uploads: `POST /messaging/{connection}/media/uploads`. | same | `messaging/send`, `messaging/media` |
| `send-sticker` | `content.sticker` (`url` or `base64`). | same | `messaging/send`, `messaging/stickers` |
| `send-location`, `send-contact` | `content.location:{lat,long,address}`, `content.contact:{vcard}`. | same | `messaging/send` |
| `send-poll` | `content.poll:{title, options (2-12), multiSelect}` | same | `messaging/send` |
| `reply` | `quotedMessage:{id}` (Polymorfa message id). | same | `messaging/send` |
| `forward` | No forward-by-id call. Send the content again with `isForwarded:true`. | different | `messaging/send` |
| `click-button`, buttons and lists (Baileys engine only) | `content.buttons` (`reply`, `url`, `call`, `copy`, `catalog`) and `content.list`. Linked devices: up to 10 controls, up to 3 CTAs. Cloud API: 1 to 3 `reply` buttons only; richer controls need an approved template. Incoming choices arrive as `button_reply`, `list_reply` or `native_flow_response`; match on `replyChoice.id`. | more | `messaging/send`, `messaging/receive` |
| `react` | `POST /messaging/{connection}/messages/react`. | same | `messaging/send` |
| `edit`, `delete` | `PUT` and `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` (scope `chats:manage`). Linked device only. | same | `messaging/send` |
| `send-template` (OpenWA text templates) | Polymorfa has no stored text templates for linked devices. Cloud API templates: `content.template` plus template CRUD. | different | `messaging/templates` |
| `send-bulk`, batch status and cancel | Campaigns: `POST /platform/campaigns`, audiences, opt-outs, A/B. Pro tier. | more | `campaigns` |
| `send-product` | `content.product`, `content.productList`; needs a Business App Connection. | more | `connections/catalog` |
| `Idempotency-Key` on single sends (kept 24 hours) | `Idempotency-Key` header on every send, kept 1 hour. | same | `development/idempotency` |
| Send pacing (`SEND_PACING_ENABLED`), typing simulation, bulk delays | Project Safe Mode: `pacing`, `typing`, `presence`, `reads`. Standard or Pro only. Plus warm-up allowance and the new-chat cap. | more | `safety/safe-mode` |
| Status posts | Not offered. | gap | none |

### 1.3 Groups, channels, labels and contacts

| OpenWA capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Groups: create, manage, join by invite code, settings | `/messaging/{connection}/groups`: create, `participants/add|remove`, `admin/promote|demote`, `subject`, `description`, `picture`, `invite-code`, `join`, `settings/*`, `leave`. | same | `messaging/contacts-and-groups` |
| Group join requests (`group.join_request`) | Not on the linked-device API. | gap | none |
| Channels and newsletters | `/messaging/{connection}/channels`: create, follow, unfollow, mute, read, delete. Admin tools and renaming are not offered. | different | `messaging/channels` |
| Labels | `GET|POST /messaging/{connection}/labels`, `PUT|DELETE .../labels/{labelId}`, `GET|PUT .../labels/chats/{conversation}` (PUT replaces the full set). | same | `messaging/linked-device-controls` |
| Contacts, block and unblock, number check | `GET .../contacts`, `.../contacts/{contactId}/block`, `/unblock`, `GET .../contacts/check?phone=` (up to 1,000). Address book writes are not offered. | same | `messaging/user-identities` |
| Chats and stored messages (OpenWA database) | `GET .../chats`, `GET .../chats/{conversation}/messages`. Needs hosted message storage (beta) and expires by retention. | different | `messaging/history` |

### 1.4 Calls

| OpenWA capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `call.received`, `call.accepted`, `call.rejected`, `call.missed` events | Same event names, plus `call.ended` and the rest of the `call.*` family. | more | `calls/how-calls-work` |
| Reject a call, per-session auto-reject (Baileys only) | `POST /messaging/{connection}/calls/{callId}/reject`; `PUT /platform/connections/{connection}/call-settings` with `callsEnabled:false` declines every incoming call. | same | `calls/server` |
| Placing or answering calls | `POST /messaging/voip/calls` places a call; browser calls use client tokens; SIP trunks run both directions. | more | `calls/server`, `calls/web`, `calls/sip-trunks` |

### 1.5 Automation and tools

| OpenWA capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| MCP at `POST /mcp` (25 read tools, 52 with writes) | Hosted MCP server at `https://api.polymorfa.com/mcp` with 200+ tools, Bearer credential. It cannot return QR or pairing codes. | more | `development/mcp` |
| Swagger at `/api/docs` | OpenAPI 3.1 specs for Messaging, Platform and Graph, with a Try it playground in the docs. | more | `api/overview` |
| Chatwoot and Typebot plugins, n8n community nodes | Not offered. Connect through the API, webhooks or MCP. | gap | `development/webhooks` |
| Auto-reply rules | Not offered as a feature. Build the reply in your webhook handler. | gap | `development/webhooks` |
| Dashboard | The Polymorfa Console. | same | `get-started/console` |

## 2. Identifiers and credentials

### 2.1 Credentials

| OpenWA | Polymorfa | Notes |
| --- | --- | --- |
| `X-API-Key` (roles ADMIN, OPERATOR, VIEWER) | `Authorization: Bearer <credential>` | See credentials below. |
| `allowedSessions`, `allowedChats` on a key | Scopes on the key, project confinement, expiry, service accounts, rotation. | No per-chat or IP allowlist. |
| Dashboard login with an API key | Console sign-in with a Polymorfa account. | |
| Browser use of an API key | Client token `pmfa_ct_...`, minted by your server with `POST /platform/client-tokens`, bound to one Connection and an action list. | The issuing credential needs the scopes it grants. |

Credentials: team key `pmfa_...` (all projects), project token `pmfa_pt_...` (one project, the least-privilege replacement for a session-scoped key), client token `pmfa_ct_...`. A migration agent cannot mint keys. Ask the human to create a project token with `messages:write`, `contacts:read`, `webhooks:manage`, `connections:manage` and the group, contact and chat scopes each reference page lists, then set `POLYMORFA_KEY`.

### 2.2 Phone numbers and chat ids

- OpenWA `chatId`: digits plus a suffix, `15550001111@c.us`, groups `@g.us`, privacy ids `@lid`. Polymorfa `conversation.phoneNumber`: E.164 with `+`, `+15550001111`. The Graph API `to` takes digits without `+`.
- The returned `phoneNumber` is WhatsApp's resolved number and can differ from the input. Match conversations by `conversation.id` per Connection.
- Groups and `@lid` ids do not convert. Polymorfa group ids are opaque decimals. Build a map once with `GET /messaging/{connection}/groups` and store `group.id`. Reply to hidden-number senders with `conversation.id`.
- OpenWA `sessionId` becomes the Connection id. WhatsApp's message id is in `whatsapp_ids`. Keep both when migrating stored threads.

## 3. Webhook migration

### 3.1 Transport

| Topic | OpenWA | Polymorfa |
| --- | --- | --- |
| Registration | `POST /api/sessions/{id}/webhooks` per session with `url`, `events`, `secret`, `headers`, `retryCount`, `filters` | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` or `meta`), `retryPolicy`, `enabled`, custom headers. Needs `webhooks:manage`. Each mutation needs an `Idempotency-Key`. |
| Authentication | `X-OpenWA-Signature: sha256=<hex>`, HMAC-SHA256 with the webhook secret | HMAC-SHA256 over the exact raw body. `native`: `X-Webhook-Signature: <lowercase hex>`. `meta`: `X-Hub-Signature-256: sha256=<hex>`. Constant-time compare. Secret returned once on create; rotate with `POST .../secret-rotations`. |
| Retries | Up to 5 total attempts, exponential backoff from 5 seconds, default 3 attempts | Up to 8 attempts over 24 hours at 30 s, 2 min, 10 min, 1 h, 4 h, 12 h and 24 h. Retries on network error, timeout, `408`, `429`, `5xx`. |
| Timeout | 10 seconds | 30 s per attempt, up to 3 redirects. Respond fast, process later. |
| Trace and dedupe | `X-OpenWA-Idempotency-Key`, `X-OpenWA-Delivery-Id`, `X-OpenWA-Retry-Count` | `X-Polymorfa-Delivery-ID`, `X-Polymorfa-Delivery-Attempt`. The event `id` is stable across retries. Delivery is at least once and unordered. |
| Redelivery | Delivery failures list and redrive | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |
| Filters | `filters` on sender, chat, body, type, group | Event-type subscription only. Filter in your handler. |
| Event stream | WebSocket `/events` | `GET /platform/projects/{projectId}/events/stream` (SSE, beta) |

### 3.2 Envelope

```json
{
  "id": "<event id>",
  "connection": "739182640518203",
  "timestamp": "2026-10-19T10:05:00.000Z",
  "event": "message.received",
  "payload": { }
}
```

OpenWA's `event`, `sessionId`, `timestamp`, `idempotencyKey`, `deliveryId` and `data` become `event`, `connection`, `timestamp`, the envelope `id` and `payload`.

### 3.3 Events

| OpenWA event | Polymorfa event | Notes |
| --- | --- | --- |
| `message.received` | `message.received`, plus `message.reaction`, `message.vote`, `message.edited`, `message.revoked` | Chat becomes `payload.conversation.id`; group senders are in `payload.conversation.sender`. |
| `message.sent` | `message.sent` | |
| `message.ack`, `message.receipt` | `message.ack` (`type`: `delivered`, `read`, `played`, `error`) | No per-recipient group receipt event found. |
| `message.failed` | `message.failed` | Read its `error` and `code`. |
| `message.revoked`, `message.reaction`, `message.edited` | `message.revoked`, `message.reaction`, `message.edited` | |
| `poll.vote` | `message.vote` | |
| `session.qr`, `session.authenticated`, `session.status`, `session.disconnected`, `session.reconnect_loop` | `connection.status`, `connection.connected`, `connection.logged_out` | Pairing uses QuickLink. |
| `session.restriction` | `connection.restriction_updated` | |
| `presence.update` | `presence.update` | Opt-in per project. |
| `group.join`, `group.leave`, `group.update` | `group.participant`, `group.update` | `group.join_request` has no equivalent. |
| `call.received`, `call.accepted`, `call.rejected`, `call.missed` | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended` | |
| Button and list replies | `message.received` with `button_reply`, `list_reply` or `native_flow_response` | Key on `replyChoice.id`. |

Media events carry a `media` reference, not inline content.

### 3.4 What a migrating handler must change

1. Verify `X-Webhook-Signature` on the raw bytes first. This replaces the `X-OpenWA-Signature` check.
2. Read the body under `payload` and the type under `event`.
3. Key people by `conversation.id`; stop parsing `@c.us`, `@g.us` and `@lid`.
4. Replace the OpenWA message id with `payload.id` for actions; store `whatsapp_ids`.
5. Respond 2xx within 30 s after a durable save, dedupe on the envelope `id`, and accept reordering.
6. Subscribe to specific `eventTypes`.
7. Handle new events: `message.failed`, `connection.restriction_updated`, `bansafe.*`.

## 4. Gaps and behaviour differences a migrating agent must handle

Gaps (not offered):

1. Status posts.
2. A per-session proxy.
3. Per-key allowlists of IP addresses and chats.
4. Chatwoot and Typebot plugins, and auto-reply rules.
5. Group join-request approval on linked devices.
6. Importing an OpenWA session. Pair again.

Behaviour differences:

- **Queue on disconnect.** Polymorfa refuses a send to a disconnected Connection: `503 connection_not_ready` (synchronous) or `message.failed` with `connection_not_connected` (asynchronous, with `Prefer: respond-async`). The migrating app needs its own outbox. Use `Idempotency-Key` (1-hour window) so a retry cannot send twice. Do not retry on `bansafe_send_outcome_unknown`; read the message state first.
- **First messages to people who never wrote.** Outside Campaigns, a first message to such a contact is refused (`bansafe_cold_blocked`, `403`), and adding that person to a group is refused too. Route outreach through Campaigns (Pro) or message people who wrote first.
- **Pacing is enforced.** Warm-up allowance (`bansafe_daily_allowance_reached`, `429`), throttle (`bansafe_throttled`, `429`, `Retry-After`) and the WhatsApp new-chat cap (`new_chat_limit_reached`, `429`). Respect `Retry-After`.
- **Delays.** OpenWA's pacing and typing simulation map to project Safe Mode (`pacing`, `typing`, `presence`, `reads`), all off by default, Standard or Pro only, owner or admin to change. Contacts see presence, typing and read receipts, which cannot be undone.
- **Media.** OpenWA returns most media inline in API and webhook responses. Polymorfa keeps no attachment files. Download on webhook receipt with `GET /messaging/media/{id}`, or save to your own bucket with `POST /messaging/media/{id}/download-and-save`.
- **IDs.** Everything is an opaque decimal string. Do not parse or cast it. Remap stored group ids by listing groups.
- **Hosted history.** OpenWA stores messages in the user's own database. Polymorfa history needs hosted message storage (beta) and is bounded by retention. Export what the user needs from OpenWA before shutting it down.
- **Official API.** OpenWA connects only through reverse-engineered clients. On Polymorfa a Cloud API Connection uses the same API as a linked-device Connection; the Connection you address decides the route. Cloud API onboarding is in beta.
- **Hosting.** Polymorfa runs the sessions. The user keeps no servers, database or Helm chart for WhatsApp, and stops the OpenWA deployment only after every number runs on Polymorfa.
- **Pairing.** Keep a working OpenWA session logged in until its Polymorfa connection is paired. A phone has a limit on linked devices, so check there is room for one more.
