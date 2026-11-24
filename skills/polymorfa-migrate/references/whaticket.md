# Whaticket reference for polymorfa-migrate

Maps the Whaticket API (https://api.whaticket.com/api/v1, definition at https://api.whaticket.com/api/v1/openapi.json) to Polymorfa. Checked on 24 November 2026 against Whaticket's public help center, pricing page and OpenAPI definition, and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/whaticket.

Whaticket is a team inbox with an API. Polymorfa is an API with no hosted agent inbox. Ask the user which inbox behavior their code depends on before you map anything.

## Requests and credentials

| Whaticket | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `Authorization: Bearer <token>`, token linked to a profile (Integrações > Tokens) | `Authorization: Bearer <API key>` with selected scopes; short-lived client tokens for browsers | more | `development/api-keys`, `development/client-tokens` |
| `GET /me` | Any read with the key, such as `GET /platform/connections` | different | `development/api-keys` |
| Phone `number` as digits, no plus sign | `conversation.phoneNumber` with a plus sign, such as `+5511999990000` | different | `messaging/send` |
| 600 requests a minute per company | Respect `Retry-After` on `429` | different | `api/errors` |

## Connections

| Whaticket | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| WhatsApp QR connection | QuickLink, or `GET /messaging/{connection}/pair/qr` and `POST /messaging/{connection}/pair/code` with direct pairing | same | `connections/quicklink`, `connections/direct-pairing` |
| `GET /connections`, `GET /connections/{id}` | `GET /platform/connections`, `GET /platform/connections/{connectionId}` | same | `connections/manage` |
| `PATCH /whatsapps/start/{whatsappId}` (restart a disconnected QR session) | `POST /platform/connections/{connectionId}/restart`; returns `202` with an operation id, then wait for `connection.status`. Also `stop` and `logout`. | same | `connections/manage` |
| `PATCH /connections/{id}` (greeting, farewell, chatbot, AI settings) | No equivalent. These are inbox settings. | gap | none |
| WABA and Coexistence connections | Cloud API and coexistence through Embedded Signup, in beta and needing access | same | `connections/cloud-api-setup` |

## Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?}`. Add an `Idempotency-Key` header.

| Whaticket | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `POST /tickets/{ticketId}/messages` with `body` | `content.text` to the same person | same | `messaging/send` |
| `POST /messages` to one contact | Send call, one recipient | same | `messaging/send` |
| `POST /messages` to up to 999 contacts (creates a campaign) | Campaign with an audience, opt-outs and per-recipient status; Pro connections | different | `campaigns/send` |
| `POST /medias`, then `mediaKey` and `mediaType` (image, video, audio, document) | `content.image`, `content.video`, `content.voice`, `content.file` with `url` or `base64` | different | `messaging/send`, `messaging/media` |
| `templateId` and `variables` (WABA) | `content.template`; template create, preview and submit to Meta | same | `messaging/templates` |
| `quotedMsgId` | `quotedMessage.id` | same | `messaging/send` |
| `sendAt` (scheduled reply) | No scheduled single send. Schedule in the application, or use a Campaign with a scheduled start. | gap | `campaigns/send` |
| `isNote` (internal note) | Not offered. | gap | none |
| Replies need a contact message in the last 7 days | Linked-device sends have no such window; Cloud API connections follow Meta's 24-hour service window and need templates outside it | different | `messaging/templates` |

## Receiving and events

| Whaticket | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| No event routes. Poll `GET /tickets` and `GET /tickets/{ticketId}/messages`. | Webhook event `message.received` | more | `development/webhooks` |
| Fluxos action "Enviar webhook" and chatbot step "Chamar webhook" (payload not documented) | One signed endpoint (`X-Webhook-Signature`, HMAC-SHA256 of the raw body); up to 8 attempts over 24 hours; delivery log and replay | more | `development/webhooks` |
| Message `ack` field | `message.ack`, `message.sent`, `message.failed` | more | `api-events` |
| Connection status | `connection.status`, `connection.connected`, `connection.logged_out` | more | `api-events` |

## Chats, contacts and tags

| Whaticket | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `GET /tickets`, `GET /tickets/{id}` | `GET /messaging/{connection}/chats`, `GET /messaging/{connection}/chats/{conversation}`; beta, needs hosted message storage and joining the history beta | different | `messaging/history` |
| `GET /tickets/{id}/messages` | `GET /messaging/{connection}/chats/{conversation}/messages`; or store events as they arrive | different | `messaging/history` |
| Contact tags | Labels attached to chats: `GET/POST /messaging/{connection}/labels`, `PUT /messaging/{connection}/labels/chats/{conversation}` | different | `messaging/contacts-and-groups` |
| `POST /contacts`, `create-or-update` with `customFields` | Contacts are read from WhatsApp. For campaign attributes use audience profiles. | different | `campaigns/audience-profiles` |

## Inbox features with no equivalent

Resolve, snooze, transfer, assign, queues (departments), Kanban stages, internal chat and mentions, quick replies, chatbot menus, knowledge base and the Wäbot agent, away periods and conversation reports. Polymorfa does not offer them. The application keeps this state, and the UI Kit (`ui-kit/inbox`) has inbox components to build screens. Whaticket's Web Chat, Instagram, Facebook and Telegram channels also have no equivalent: Polymorfa connects WhatsApp.

## Behavior to carry over

- A send to a disconnected Connection fails at once with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it.
- Whaticket ids (ticket, contact, connection) do not carry over. Polymorfa ids are opaque strings (`messaging/ids`).

## AI agents

Whaticket offers an MCP server through its connected apps tab. Polymorfa has a hosted MCP server with 150+ tools (`development/mcp`).
