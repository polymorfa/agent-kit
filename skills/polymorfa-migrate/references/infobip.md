# Infobip reference for polymorfa-migrate

Maps Infobip WhatsApp (https://www.infobip.com/docs/whatsapp, OpenAPI at https://api.infobip.com/platform/1/openapi/whatsapp) to Polymorfa. Checked on 24 November 2026 against Infobip's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/infobip.

## Requests and credentials

Infobip: `https://{subdomain}.api.infobip.com/whatsapp/1/...` on the account's own base URL, with `Authorization: App <API key>` (Basic and OAuth 2.0 also exist). The sending number goes in the body as `from`; each send carries an optional `messageId`, `callbackData` and `notifyUrl`.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask the user who owns each WhatsApp Business Account (their own, or one Infobip created for them) before planning the move. A number registered to Cloud API with another provider keeps that provider's registration PIN; the user resolves it with Infobip first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Infobip capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Sender added through Embedded Signup | Connection, created through a QuickLink with Meta Embedded Signup | different | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence | Embedded Signup option to keep using the WhatsApp Business app | same | `connections/cloud-api-setup` |
| Tech Provider onboarding in the user's own app (Facebook Login, 200 clients a week per solution) | QuickLink hosted page and the Customers API | more | `connections/quicklink`, `customers` |
| Sender business info and logo | `/{phone-number-id}/whatsapp_business_profile` | same | `connections/business-profile` |
| `/whatsapp/1/message/text`, `image`, `video`, `audio`, `document`, `sticker`, `location`, `contact` | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| `/message/interactive/buttons`, `list`, `url-button`, `location-request` | Same endpoint, interactive body | same | `messaging/send` |
| `/message/interactive/media-carousel` | Carousel through an approved template on Cloud API. Free-form carousels exist on linked-device Connections | different | `messaging/send` |
| `/message/template` | Same endpoint with `type: "template"` | same | `messaging/templates` |
| Templates: create, list, edit, delete | `POST`, `GET`, `DELETE /{waba-id}/message_templates`; project templates also have preview. Edit is not on the Graph API | different | `messaging/templates` |
| WhatsApp Flows: create, publish, deprecate, send | `/{waba-id}/flows` lists and creates; edit and publish in the Flow builder; Flow sends use the messages endpoint | more | `messaging/flows` |
| `/message/interactive/product`, `multi-product`, catalogs | `/{waba-id}/product_catalogs`, `/{phone-number-id}/whatsapp_commerce_settings` | same | `connections/catalog` |
| `/message/interactive/order-details`, `order-status` | Only for teams with access, from Cloud API Connections that Meta made eligible for payments in Brazil; others get error `131026` | different | `connections/catalog` |
| Mark as read | `status: "read"` on the messages endpoint (Cloud API Connections) | same | `messaging/send` |
| Inbound media download, delete media | `POST /{phone-number-id}/media`, `GET /{media-id}`, `DELETE /{media-id}` | same | `messaging/media` |
| Stored media | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Sender quality | Not verified for Cloud API Connections. Check the docs before relying on it | gap | none |
| Conversions API submissions | Not offered | gap | none |
| Groups | Not in Infobip's WhatsApp API. Groups exist on Polymorfa linked-device Connections under `/messaging/{connection}/groups` | different | `messaging/contacts-and-groups` |
| Conversations, Moments, Answers, other channels | Not offered | gap | none |

## Calls

| Infobip capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Enable and disable calling on a sender | Call settings on the Connection | same | `calls/how-calls-work` |
| Inbound and outbound calls to a WebRTC user, IVR or Calls API application | Calls in the browser, from server code and over SIP, in both directions. Set `hostCloudApiCalls` to `true` on a Cloud API Connection to have Polymorfa Calls answer | more | `calls/server` |
| SIP trunking to an SBC or PBX | SIP trunks (`PUT /platform/connections/{connection}/call-settings`) | same | `calls/sip-trunks` |
| Call permission request message and permission lookup | `callPermissionRequest` content, permission checks, do-not-call list | same | `calls/permissions` |
| Meta call actions through your own stack | `POST /{phone-number-id}/calls` takes Meta's actions and forwards them unchanged | same | `calls/server` |

Polymorfa does not record calls.

## Webhooks

Infobip sends delivery and seen reports to a global URL or to `notifyUrl` on one message, and delivers `DELIVERY`, `SEEN`, `CLICK`, `INBOUND_MESSAGE` and `PAYMENT_STATUS` through Subscriptions, which support Basic, HMAC, OAuth and mTLS authentication. It retries up to 20 times over about 41.5 hours and does not keep events.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Infobip | Polymorfa | Status |
| --- | --- | --- |
| Delivery report | `message.ack`, `message.failed`, or Meta `statuses` in the meta format | same |
| Seen report | `message.ack` | same |
| `INBOUND_MESSAGE` | `message.received`, or Meta `messages` in the meta format | same |
| `callbackData`, `notifyUrl` per message | No equivalent. Match events to sends by message ID | gap |
| `CLICK` | Not verified. Check the webhook docs before relying on it | not verified |
| `PAYMENT_STATUS` | Not verified. Check the webhook docs before relying on it | not verified |
| Call events | `call.received`, `call.accepted`, `call.missed`, `call.ended` | same |

## Differences to agree with the user

- Infobip request shapes change once to Meta's. Rewrite sends, then follow Meta's documentation.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- Infobip `messageId`, `mediaId`, `flowId` and the account base URL do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Download received media when the event arrives; upload outgoing media again.
- Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Infobip one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Cancel the Infobip sender only after the number runs on Polymorfa.
