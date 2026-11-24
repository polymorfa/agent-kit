# WAHA reference for polymorfa-migrate

Maps WAHA (https://waha.devlike.pro) to Polymorfa. Checked on 24 November 2026 against WAHA's published documentation and release list, and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/waha.

WAHA is self-hosted software the user runs in Docker, with four active engines (WEBJS, WPP, NOWEB, GOWS). Request and webhook shapes differ by engine. Ask which engine each session runs before you map anything.

## Requests and credentials

| WAHA | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `https://<host>/api/...` with `X-Api-Key` (admin key or session key) | `https://api.polymorfa.com/messaging/{connection}/...` with `Authorization: Bearer <API key>` and selected scopes | more | `development/api-keys` |
| `session` in the body or path | `{connection}` in the path | different | `messaging/send` |
| Session key or `?x-api-key=` for a browser | Short-lived client token scoped to one Connection | more | `development/client-tokens` |
| `chatId` `15550001111@c.us`, `@lid`, `@g.us`, `@newsletter` | `conversation.phoneNumber` with a plus sign for a first send; opaque ids afterwards | different | `messaging/ids` |

## Sessions and pairing

| WAHA | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `POST /api/sessions` | Create a QuickLink: `POST /messaging/quicklinks`; the Connection ID is returned as `data.connection` | different | `connections/quicklink` |
| `GET /api/{session}/auth/qr` | QuickLink, or `GET /messaging/{connection}/pair/qr` (needs direct pairing access) | same | `connections/direct-pairing` |
| `POST /api/{session}/auth/request-code` | QuickLink pairing code, or `POST /messaging/{connection}/pair/code` | same | `connections/direct-pairing` |
| Control key for your own QR page | QuickLink hosted page, optionally branded | same | `connections/quicklink` |
| Session status (`WORKING`, `SCAN_QR_CODE`, `FAILED`) | `GET /platform/connections/{connectionId}` and `connection.status` | more | `connections/manage` |
| `POST /api/sessions/{session}/restart`, `stop`, `logout` | `POST /platform/connections/{connectionId}/restart`, `stop`, `logout`; each returns `202` with an operation id | same | `connections/manage` |
| `DELETE /api/sessions/{session}` | `DELETE /platform/connections/{connectionId}` | same | `connections/manage` |
| Per-session proxy | No equivalent | gap | none |
| Export or backup of session storage | WAHA documents none. A Baileys `SignalStoreSnapshot` imports through the API and a whatsmeow device store through assisted migration, only if the user already holds one | different | `connections/import-connections` |

Never run the source and an imported copy at the same time.

## Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?}`. Add an `Idempotency-Key` header; WAHA has none.

| WAHA | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `/api/sendText` | `content.text` | same | `messaging/send` |
| `/api/sendImage`, `sendVideo`, `sendVoice`, `sendFile`, `sendSticker` | `content.image`, `video`, `voice`, `file`, `sticker` (`url` or `base64`) | same | `messaging/send`, `messaging/media` |
| `/api/sendLocation`, `/api/sendContactVcard` | `content.location`, `content.contact` | same | `messaging/send` |
| `/api/sendList`, buttons, polls | `content.list`, `content.buttons`, `content.poll` | same | `messaging/send` |
| `reply_to` | `quotedMessage.id` | same | `messaging/send` |
| `mentions` | `mentions` (user ids) | different | `messaging/send` |
| Edit and delete a message | `PUT` and `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `/api/reaction`, `/api/star`, `/api/sendSeen` | `POST .../messages/react`, `.../messages/star`, `.../messages/seen` | same | `messaging/send` |
| `/api/startTyping`, `/api/stopTyping` | `POST .../messages/typing` | same | `messaging/send` |
| `/api/forwardMessage` | `isForwarded: true` on a new send; no forward-by-id | different | `messaging/send` |
| Status updates (`/api/{session}/status/...`) | Not offered | gap | none |

## Webhooks and events

WAHA signs the raw body with HMAC-SHA512 in `X-Webhook-Hmac` (algorithm in `X-Webhook-Hmac-Algorithm`), with `constant`, `linear` or `exponential` retries per webhook. Polymorfa signs with HMAC-SHA256 in `X-Webhook-Signature`, retries up to 8 times over 24 hours, and keeps a delivery log with replay.

| WAHA event | Polymorfa event | Status | Docs page |
| --- | --- | --- | --- |
| `message`, `message.any` | `message.received`; `message.sent` or `message.failed` for own sends | more | `development/webhooks`, `api-events` |
| `message.ack` | `message.ack` | same | `api-events` |
| `message.reaction`, `message.edited`, `message.revoked` | same names | same | `api-events` |
| `poll.vote` | `message.vote` | same | `api-events` |
| `session.status` | `connection.status`, `connection.connected`, `connection.logged_out` | more | `api-events` |
| `presence.update` | `presence.update` | same | `api-events` |
| `group.v2.*` | `group.update`, `group.participant` | different | `api-events` |
| `call.received`, `call.accepted`, `call.rejected` | the `call.*` events | more | `calls` |
| WebSocket `/ws` | Server-sent event stream, beta, resumable with `Last-Event-ID` | different | `development/event-streams` |

Payloads carry an engine-specific `_data` field. Polymorfa has no equivalent; map the fields the code reads.

## Groups, contacts, channels and history

| WAHA | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Groups: create, participants, admins, settings, invite code, picture, join and leave | The same operations under `/messaging/{connection}/groups` | same | `messaging/contacts-and-groups` |
| Group join requests (list, approve, reject) | Not offered | gap | none |
| Contacts, `check-exists`, LID and phone mapping | Contact lookup and identity resolution; ids are opaque | different | `messaging/contacts-and-groups`, `messaging/ids` |
| Labels | `GET/POST /messaging/{connection}/labels`, attach to chats | same | `messaging/contacts-and-groups` |
| Channels (`@newsletter`): create, search, follow, mute, send | Create, follow, mute and read | different | `messaging/channels` |
| `GET /api/{session}/chats` and messages | Message history API; beta, needs opt-in and hosted message storage | different | `messaging/history` |
| Media in `media.url`, local files kept 180 seconds by default, or PostgreSQL or S3 | Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage. Polymorfa keeps no copy | different | `messaging/media` |

## Calls

WAHA reports incoming calls and can reject them (`POST /api/{session}/calls/reject`). Polymorfa rejects with `POST /messaging/{connection}/calls/{callId}/reject`, and also places and answers calls in a browser, from server code and over SIP (`calls`, `calls/sip-trunks`).

## Behavior to carry over

- A send to a disconnected Connection fails at once with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it.
- WAHA ids do not carry over. Polymorfa ids are opaque strings (`messaging/ids`).
- Stop the WAHA session for a number once it moves.

## AI agents

WAHA offers an MCP app, one per session. Polymorfa has a hosted MCP server with 200+ tools (`development/mcp`).
