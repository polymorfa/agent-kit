# 360dialog reference for polymorfa-migrate

Maps 360dialog (https://docs.360dialog.com) to Polymorfa. Checked on 24 November 2026 against 360dialog's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user), `not verified` (not checked; read the docs before relying on it).

The human guide is https://docs.polymorfa.com/migrate/360dialog.

## Requests and credentials

360dialog: `https://waba-v2.360dialog.io/<path>`, for example `POST /messages`, `POST /media`, `GET /{media-id}`, `POST /marketing_messages`. The `D360-API-KEY` header carries a key that belongs to one phone number, so the path never names the number. The sandbox is `https://waba-sandbox.360dialog.io`: 25 messages, to the sender's own number only. Partner integrations use a separate Partner API with its own key.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. The phone number ID is part of the path, so look it up for each 360dialog key. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask who owns each WhatsApp Business Account before planning the move. A number registered to Cloud API with another provider keeps that provider's registration PIN; the user resolves it with 360dialog first. Polymorfa Cloud API onboarding is a beta that needs team access. Cancelling a 360dialog subscription does not release the number, and templates stay in 360dialog's messaging account.

## Mapping

| 360dialog capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Channel (Cloud API number), created with Embedded Signup in the Hub | Connection, created through a QuickLink with Meta Embedded Signup | different | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence | Embedded Signup option to keep using the WhatsApp Business app | same | `connections/cloud-api-setup` |
| Partner Platform and Partner API (channels, keys, onboarding) | Customers API, with a monthly cap and pairing links per customer | more | `customers/index` |
| `POST /messages` (text, media, location, contacts, reactions, interactive) | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| Media carousel, call-to-action URL button | Same endpoint, interactive body. Carousel through an approved template on Cloud API; free-form carousels exist on linked-device Connections | same | `messaging/send` |
| Templates: create, list, delete, send | `POST`, `GET`, `DELETE /{waba-id}/message_templates`, and `type: "template"` sends; project templates also have preview | more | `messaging/templates` |
| Flows API | `/{waba-id}/flows` lists and creates. Update, publish and delete are not on the Graph API; use the Flow builder and project drafts | different | `messaging/flows` |
| Catalogs, single and multi-product messages | `/{waba-id}/product_catalogs`, `/{phone-number-id}/whatsapp_commerce_settings`, product sends | same | `api/graph/index` |
| Marketing Messages API (`/marketing_messages`) | `/{phone-number-id}/marketing_messages`, `/{waba-id}/marketing_messages/status` | same | `api/graph/index` |
| Upload, retrieve, delete media | `POST /{phone-number-id}/media`, `GET /{media-id}`, `DELETE /{media-id}` | same | `messaging/media` |
| Received media download (rewrite the `lookaside.fbsbx.com` host to the 360dialog host, send `D360-API-KEY`, link valid 5 minutes) | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Mark as read, typing indicator | `status: "read"` on the messages endpoint (Cloud API Connections); typing through the Messaging API | same | `messaging/send` |
| Block users | `/{phone-number-id}/block_users` | same | `api/graph/index` |
| Business profile | `/{phone-number-id}/whatsapp_business_profile` | same | `connections/business-profile` |
| Conversational components | `/{phone-number-id}/conversational_automation` | same | `api/graph/index` |
| Groups API (Official Business Accounts, up to 8 participants) | Not offered for Cloud API Connections. Groups exist on linked-device Connections under `/messaging/{connection}/groups` | gap | `messaging/contacts-and-groups` |
| Hosted Inbox | Inbox and chat components for the user's own app | different | `ui-kit/inbox` |
| Inbox API (assignment, tags, resolved status) | Not offered | gap | none |
| Template analytics | Not offered | gap | none |
| Direct Send (`category: "utility"` on `/messages`) | Not verified on the Graph API | not verified | `api/graph/index` |
| Payments APIs (Brazil, India, Singapore) | Not verified | not verified | none |
| Local storage (data residency region per number) | Not verified | not verified | none |
| MCP server for the 360dialog account | Hosted MCP server with 150+ tools, and a local MCP in the CLI | more | `development/mcp` |
| Sandbox | Test connections on a simulated network, at 0 credits | more | `testing/index` |

## Calls

| 360dialog capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Calling API: the user runs SIP or WebRTC media | `POST /{phone-number-id}/calls` takes Meta's call actions unchanged. Set `hostCloudApiCalls` to `true` and Polymorfa Calls answer in the browser, server code or SIP; the Graph `/calls` endpoint then refuses to answer | more | `calls/server` |
| SIP configuration | Call settings and SIP trunks (`PUT /platform/connections/{connection}/call-settings`) | more | `calls/sip-trunks` |
| Call connect and status webhooks (ringing, accepted, rejected, terminated) | Events `call.received`, `call.accepted`, `call.missed`, `call.ended` | same | `calls/how-calls-work` |

360dialog's Calling API needs a number with a business-initiated limit of at least 2,000, and does not work on coexistence numbers. Cloud API calls are one-to-one audio. Polymorfa does not record calls.

## Webhooks

360dialog sends Meta's envelope (`object`, `entry`, `changes`, `value`) with `messages`, `statuses` and `errors` to one URL per number or per WABA, set in the Hub or with `POST /v1/configs/webhook` (number) and `POST /waba_webhook` (WABA). It documents no payload signature, only an optional custom `Authorization` header. It expects `200 OK` within 5 seconds, and Meta retries a failed delivery for up to 7 days. Coexistence adds `history`, `smb_app_state_sync` and `smb_message_echoes`.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| 360dialog | Polymorfa | Status |
| --- | --- | --- |
| `messages` (inbound) | `message.received`, or Meta `messages` in the meta format | same |
| `statuses` (sent, delivered, read, failed) | `message.ack`, `message.failed`, or Meta `statuses` in the meta format | same |
| `errors` | Meta format only. Check the webhook docs for the native equivalent | not verified |
| Call webhooks | `call.received`, `call.accepted`, `call.missed`, `call.ended` | same |
| `history`, `smb_app_state_sync`, `smb_message_echoes` (coexistence) | Not verified. Check the webhook docs before relying on them | not verified |

## Differences to agree with the user

- 360dialog requests change base URL, header and path: add the phone number ID, and replace `D360-API-KEY` with a bearer token. Bodies stay Meta's.
- Replace the Basic auth check on the webhook route with signature verification on the raw body.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- 360dialog identifiers (API keys, channel ids, media ids, call ids) do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Download received media when the event arrives; upload outgoing media again. 360dialog keeps uploaded media 30 days after last use and webhook media 7 days.
- Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the 360dialog one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Cancel the 360dialog subscription in the Hub only after the number runs on Polymorfa. The cancellation takes effect at the end of the billing month.
