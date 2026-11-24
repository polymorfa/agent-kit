# Meta Cloud API reference for polymorfa-migrate

Maps Meta's WhatsApp Business Platform Cloud API (https://developers.facebook.com/documentation/business-messaging/whatsapp) to Polymorfa. Checked on 24 November 2026 against Meta's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user), `not verified` (not checked; read the docs before relying on it).

The human guide is https://docs.polymorfa.com/migrate/meta-cloud-api.

## Requests and credentials

Meta: `https://graph.facebook.com/{version}/{phone-number-id}/...` and `/{waba-id}/...` with a system user access token. Meta bills the user's WhatsApp Business Account (WABA) per delivered message, by category and the recipient's country.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Keep the phone number IDs and WABA IDs Meta assigned; nothing about the WABA, the number or its templates moves. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask who manages the Meta assets and the registration PIN of each number before planning the move. Polymorfa Cloud API onboarding is a beta that needs team access. A number already registered to Cloud API keeps its PIN; Polymorfa stops before it replaces a PIN it does not hold. Meta keeps billing messages and calls to the user's WABA, and Polymorfa does not remove those charges.

## Mapping

| Meta Cloud API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Embedded Signup in the user's own app, after App Review | Connection created through a QuickLink with Meta Embedded Signup | different | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence with the WhatsApp Business app | Embedded Signup option to keep using the WhatsApp Business app, with history, contact and echo webhooks | same | `connections/cloud-api-setup` |
| Tech Provider program, onboarding other businesses | Customers API, with pairing links and a monthly cap per customer. Own Meta app through Branded QuickLink | different | `customers/index`, `connections/cloud-api-setup` |
| System user access token | Team key or project token in the `Authorization` header | more | `development/api-keys` |
| `POST /{phone-number-id}/messages` (text, media, location, contacts, reactions, interactive) | Same path and body under the Graph base URL | same | `messaging/send`, `api/graph/index` |
| Template messages (`type: "template"`) | Same endpoint and body | same | `messaging/templates` |
| `POST`, `GET`, `DELETE /{waba-id}/message_templates` | Same paths; project templates also have preview and submit | more | `messaging/templates` |
| WhatsApp Flows (`/{waba-id}/flows`) | Graph lists and creates Flows. Edit and publish drafts in the Flow builder or with project drafts | different | `messaging/flows` |
| Catalogs and commerce settings | `/{waba-id}/product_catalogs`, `/{phone-number-id}/whatsapp_commerce_settings` | same | `api/graph/index` |
| Marketing Messages API | `/{phone-number-id}/marketing_messages`, `/{waba-id}/marketing_messages/status` | same | `api/graph/index` |
| Media upload, retrieve, delete | `POST /{phone-number-id}/media`, `GET /{media-id}`, `DELETE /{media-id}` | same | `messaging/media` |
| Received media (media ID in a webhook lasts 7 days, URL lasts 5 minutes) | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Mark as read, typing indicator | `status: "read"` on the messages endpoint (Cloud API Connections); typing through the Messaging API | same | `messaging/send` |
| Business profile, block users, QR codes, conversational components | `whatsapp_business_profile`, `block_users`, `message_qrdls`, `conversational_automation` | same | `api/graph/index` |
| Phone number registration (`register`, `deregister`, `request_code`, `verify_code`) | Same paths, forwarded to Meta, Cloud API Connections only | same | `connections/cloud-api-setup` |
| `subscribed_apps` | Same path, forwarded to Meta. Does not create Polymorfa webhooks | same | `development/webhooks` |
| Business-scoped user IDs and usernames | `conversation.id`, `phoneNumber`, `bsuid` and `username`; send to a BSUID with `recipient` on Cloud API Connections | same | `messaging/ids`, `messaging/user-identities` |
| Groups API (Official Business Accounts, up to 8 participants) | Not offered for Cloud API Connections. Groups exist on linked-device Connections under `/messaging/{connection}/groups` | gap | `messaging/contacts-and-groups` |
| Messaging limits, quality rating, throughput | Set by Meta, unchanged. Polymorfa checks quality at setup and reports a drop in a running campaign | different | `connections/cloud-api-setup`, `campaigns/index` |
| Template analytics | Not verified | not verified | none |
| Payments APIs | Not verified | not verified | none |
| Public test number | Test connections on a simulated network, at 0 credits | more | `testing/index` |

## Calls

| Meta capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Calling API actions `connect`, `pre_accept`, `accept`, `reject`, `terminate` with your own WebRTC or SIP media | `POST /{phone-number-id}/calls` takes Meta's call actions unchanged. Set `hostCloudApiCalls` to `true` and Polymorfa Calls answer in the browser, server code or SIP; the Graph `/calls` endpoint then refuses to answer | more | `calls/server` |
| SIP configuration | Call settings and SIP trunks (`PUT /platform/connections/{connection}/call-settings`) | more | `calls/sip-trunks` |
| Call permission requests | Permission requests, a do-not-call list and blocked country codes | same | `calls/permissions` |
| Call webhooks | Events `call.received`, `call.accepted`, `call.missed`, `call.ended` | same | `calls/how-calls-work` |

Meta's business-initiated calling needs a messaging limit of at least 2,000 and is unavailable for business numbers in the US, Canada, Egypt, Vietnam and Nigeria. Cloud API calls are one-to-one audio. Polymorfa does not record calls.

## Webhooks

Meta posts the `object/entry/changes/value` envelope to the callback URL set in the Meta app. It answers a `GET` handshake with `hub.verify_token`, signs each `POST` with `X-Hub-Signature-256` (HMAC-SHA256 with the app secret) and retries a failed delivery for up to 7 days with exponential backoff.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex, with the webhook's signing secret. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. No `GET` handshake is documented. See `development/webhooks`.

| Meta webhook field | Polymorfa native event | Status |
| --- | --- | --- |
| `messages` (incoming) | `message.received` | same |
| `messages` (`statuses`) | `message.ack`, `message.failed` | same |
| `calls` | `call.received`, `call.accepted`, `call.missed`, `call.ended` | same |
| `message_template_status_update`, `message_template_quality_update` | `template.status` | same |
| `account_alerts`, `account_update` | `connection.status` with `source: "meta"` | same |
| `history`, `smb_app_state_sync`, `smb_message_echoes` (coexistence) | `history.sync`, `contact.sync`, `message.echo` | same |

## Differences to agree with the user

- Change the base URL and replace the system user token with a Polymorfa credential. Bodies stay Meta's, and so do Graph API error shapes.
- Replace the hub handshake route and the app-secret signature check with a Polymorfa webhook and signature verification on the raw body. Retries last 24 hours, not 7 days; replay missed events from the delivery log.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- Meta media IDs expire (30 days uploaded, 7 days received) and Polymorfa keeps no file. Download received media when the event arrives; upload outgoing media again.
- Store people by Polymorfa conversation `id`. A phone number can be missing when a person uses a username. One-tap, zero-tap and copy-code authentication templates still need a phone number.
- Meta's per-message charges, including service replies after the first 1,000 a month on each number from 1 October 2026, stay with the user's WABA on Cloud API Connections.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Meta one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Remove the Meta webhook subscription and system user token for a number only after it runs on Polymorfa.
