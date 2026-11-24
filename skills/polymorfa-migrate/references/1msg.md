# 1MSG reference for polymorfa-migrate

Maps 1MSG (https://1msg.io/docs/reference/whatsapp) to Polymorfa. Checked on 24 November 2026 against 1MSG's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/one-msg.

## Requests and credentials

1MSG: `https://api.1msg.io/{channelId}/<method>`. The channel token goes in the JSON body (`token`), the query string (`?token=`) or an `Authorization: Bearer` header; 1MSG reads them in that order.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask the user who owns each WhatsApp Business Account (their own, or one bought through 1MSG) before planning the move. A number registered to Cloud API with another provider keeps that provider's registration PIN; the user resolves it with 1MSG first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| 1MSG capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Channel (Cloud API number) | Connection, created through a QuickLink with Meta Embedded Signup | different | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence | Embedded Signup option to keep using the WhatsApp Business app | same | `connections/cloud-api-setup` |
| Buy a WABA from 1MSG | Not offered. The user keeps their own WABA, and Meta bills it directly | different | `connections/cloud-api-setup` |
| Channel status and settings | `GET /platform/connections/{connectionId}` and the `connection.status` event | same | `connections/manage` |
| Register, request code, verify code | `register`, `deregister`, `request_code`, `verify_code` on the Graph API (Cloud API Connections only) | same | `connections/cloud-api-setup` |
| `sendMessage`, `sendFile`, `sendSticker`, `sendLocation`, `sendContact`, reactions | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| `sendList`, reply buttons, CTA URL button | Same endpoint, interactive body | same | `messaging/send` |
| `sendCarousel` | Carousel through an approved template on Cloud API. Free-form carousels exist on linked-device Connections | different | `messaging/send` |
| `sendTemplate` | Same endpoint with `type: "template"` | same | `messaging/templates` |
| Templates: create, list, remove | `POST`, `GET`, `DELETE /{waba-id}/message_templates`; project templates also have preview | more | `messaging/templates` |
| WhatsApp Flows: create, list, publish, deprecate, delete, keys | `/{waba-id}/flows` lists and creates. Update, publish and delete are not on the Graph API; use the Flow builder and project drafts | different | `messaging/flows` |
| Send a Product, catalogs, commerce settings | `/{waba-id}/product_catalogs`, `/{phone-number-id}/whatsapp_commerce_settings` | same | `api/graph/index` |
| Marketing Messages Lite, MM Lite status | `/{phone-number-id}/marketing_messages`, `/{waba-id}/marketing_messages/status` | same | `api/graph/index` |
| `uploadMedia`, `retrieveMedia`, delete media | `POST /{phone-number-id}/media`, `GET /{media-id}`, `DELETE /{media-id}` | same | `messaging/media` |
| Stored media (1MSG keeps uploaded files) | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Mark message as read | `status: "read"` on the messages endpoint (Cloud API Connections) | same | `messaging/send` |
| Get messages list | Message history, a beta that needs enrollment and hosted message storage | different | `messaging/history` |
| Block, unblock, list blocked users | `/{phone-number-id}/block_users` | same | `api/graph/index` |
| Update profile | `/{phone-number-id}/whatsapp_business_profile` | same | `connections/business-profile` |
| Conversational automation | `/{phone-number-id}/conversational_automation` | same | `api/graph/index` |
| Groups API (list, create, update, invite link, remove participants) | Not offered for Cloud API Connections. Groups exist on linked-device Connections under `/messaging/{connection}/groups` | gap | `messaging/contacts-and-groups` |
| Inbox API (conversations, assignee, open, close) | Not offered | gap | none |
| Campaigns API | Campaigns and audiences, on Pro Connections | same | `campaigns` |
| Template analytics | Not offered | gap | none |

## Calls

| 1MSG capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `initiateCall` actions `connect`, `pre_accept`, `accept`, `reject`, `terminate` | `POST /{phone-number-id}/calls` takes the same Meta actions and forwards them unchanged | same | `calls/server` |
| Your own WebRTC SDP answer | Optional. Set `hostCloudApiCalls` to `true` and Polymorfa Calls answer in the browser, server code or SIP; the Graph `/calls` endpoint then refuses to answer | more | `calls/server` |
| Calling settings, optional SIP trunk | Call settings and SIP trunks (`PUT /platform/connections/{connection}/call-settings`) | more | `calls/sip-trunks` |
| Call permission requests and replies | `callPermissionRequest` content, permission checks, do-not-call list | same | `calls/permissions` |
| Calls webhook (`type=calls`: connect, RINGING, ACCEPTED, terminate) | Events `call.received`, `call.accepted`, `call.missed`, `call.ended` | same | `calls/how-calls-work` |

Cloud API calls are one-to-one audio. Polymorfa does not record calls.

## Webhooks

1MSG callbacks: `messages`, `ack`, `groupLifecycleUpdate`, `groupParticipantsUpdate`, `smbMessageEchoes`, `calls`. Up to 5 URLs per channel. 1MSG documents no payload signature for these events.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| 1MSG | Polymorfa | Status |
| --- | --- | --- |
| `messages` | `message.received`, or Meta `messages` in the meta format | same |
| `ack` (sent, delivered, read, failed) | `message.ack`, `message.failed` | same |
| `groupLifecycleUpdate`, `groupParticipantsUpdate` | Not offered for Cloud API Connections | gap |
| `smbMessageEchoes` (coexistence) | Not verified. Check the webhook docs before relying on it | not verified |
| `calls` | `call.received`, `call.accepted`, `call.missed`, `call.ended` | same |

## Differences to agree with the user

- 1MSG request shapes change once to Meta's. Rewrite sends, then follow Meta's documentation.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- 1MSG ids (`channelId`, `mediaId`, `flowId`, `call_id`) do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Download received media when the event arrives; upload outgoing media again.
- Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the 1MSG one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Cancel the 1MSG channel only after the number runs on Polymorfa.
