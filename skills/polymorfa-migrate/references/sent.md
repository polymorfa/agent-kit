# Sent reference for polymorfa-migrate

Maps Sent WhatsApp (https://docs.sent.dm) to Polymorfa. Checked on 24 November 2026 against Sent's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/sent.

Sent is one API for SMS, MMS, RCS and WhatsApp. Its WhatsApp route runs on the customer's own WhatsApp Business Account (WABA), connected with Log in with Meta. It bills $0.015 for each person messaged in a calendar month plus message costs at destination rates. Polymorfa carries WhatsApp only: it runs the official route as Meta Cloud API Connections (beta, needs team access) and adds linked-device Connections. SMS, MMS and RCS stay on Sent.

## 1. Mapping

### 1.1 Credentials and conventions

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `https://api.sent.dm/v3/...`, `x-api-key` header or `Authorization: Bearer <key>` | `https://api.polymorfa.com/graph/whatsapp/v26.0/...` or `/messaging/{connection}/...`, `Authorization: Bearer <credential>`. Create keys in the Console | different | `api/authentication` |
| Organization key with the `x-profile-id` header to act for a sender profile | A project or team key and the Connection of each customer; Customers hold the pairing link and monthly cap | different | `customers/index` |
| `+15551234567` style phone numbers in `to` | Graph `to`: digits without a plus sign. Messaging API `conversation.phoneNumber`: E.164 with a plus sign. Keep the returned `conversation.id` | different | `messaging/ids` |
| Message, contact and template ids from Sent | Opaque string ids. None carry over; look them up again | different | `messaging/ids` |
| Rate limit of 10,000 requests a minute, headers only on a `429` | Respect `Retry-After` on a `429`; throughput and warm-up limits apply to linked-device Connections | different | `api/errors` |

### 1.2 Connecting WhatsApp

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Log in with Meta in the dashboard, on your own WABA | A Meta Cloud API Connection: create a QuickLink with `connectionPreference` `cloud`; the business completes Embedded Signup. Needs team access. Polymorfa runs readiness checks before the Connection starts | same | `connections/cloud-api-setup`, `connections/quicklink` |
| A number that no other WABA holds, including numbers registered with the WhatsApp Business app | A linked-device Connection (QR or pairing code) keeps the app working. Coexistence on Meta Cloud API keeps the Business app in use (beta) | more | `connections/index`, `connections/cloud-api-setup` |
| Sender profiles, with `POST /v3/channels/whatsapp` and a `waba_id` to add an account | Customers, with pairing links and a monthly cap for each customer, and one Connection for each customer | more | `customers/index`, `customers/pairing-links`, `connections/quicklink` |
| Sandbox mode (`sandbox: true`) | Test connections on a simulated network, 0 credits | different | `testing/test-connections` |

Pairing and Embedded Signup are done by a person. An agent cannot complete them. Sent holds the access token of the WABA the customer connected. Whether the WABA and its templates move away from Sent is a decision for the user with Meta and Sent; do not assume it.

### 1.3 Sending

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `POST /v3/messages` with `to`, `channel`, `channels`, `text` | Graph `POST /graph/whatsapp/v26.0/{phoneNumberId}/messages` with `messaging_product: "whatsapp"`, `to`, `type: "text"`, `text.body`; or `POST /messaging/{connection}/messages/send` with `content.text`. One recipient for each send | same | `api/graph/index`, `messaging/send` |
| `to` with up to 1,000 recipients | One send for each recipient in a loop, or a campaign for many recipients | different | `campaigns/send` |
| `media_urls` | `content.image`, `video`, `voice`, `file` with `url` or `base64` | same | `messaging/send`, `messaging/media` |
| `template` with `id`, `slug` or `name`, and `parameters` | `content.template` with `name`, `language`, `components`. The template must be approved in that language or the send fails with `template_not_approved` | different | `messaging/templates` |
| Templates created in the dashboard or API, submitted to Meta by Sent | Project templates: create, preview, submit (`templates:manage`); or the Graph API `/{wabaId}/message_templates` | same | `messaging/templates` |
| `channel` omitted, so Sent picks a channel and falls back to RCS or SMS | Not needed. Every Polymorfa Connection sends on WhatsApp | different | `messaging/send` |
| `scheduled_at` (1 minute to 30 days ahead) and cancelling a scheduled message | Campaigns with `scheduledAt` and `throughput.ratePerMinute`; stop or reschedule the campaign | different | `campaigns/send` |
| Free-form text only inside the 24-hour window after an inbound WhatsApp message | The same rule on Cloud API Connections: a free-form message outside the window fails with `conversation_window_closed`. Linked-device Connections need no template | more | `messaging/send` |
| Tracked short links with click events | Campaign link tracking: a short link for each recipient, on linked-device Connections, opt-in for the team | different | `campaigns/link-tracking` |
| `Idempotency-Key` on every `POST`, 24-hour cache | `Idempotency-Key` header, 1-hour receipt | same | `development/idempotency` |
| `sandbox: true` | A send from a test connection | different | `testing/test-connections` |

### 1.4 Receiving and status

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `message.received` with `text`, `channel`, `inbound_number`, `outbound_number` and the Click to WhatsApp `referral` | `message.received`: `payload.id`, `payload.conversation`, `payload.type` and the text or media fields. The `referral` object on Cloud API messages | same | `messaging/receive`, `development/webhooks` |
| `message.sent` | `message.sent` | same | `api-events` |
| `message.delivered`, `message.read` | `message.ack` type `delivered`, `read` (and `played`) | same | `api-events` |
| `message.failed` with `reason_code` and `reason` | `message.failed`, or `message.ack` type `error`; synchronous errors return an HTTP error with a stable `error.code` | different | `api/errors` |
| `message.queued`, `message.routed`, `message.scheduled`, `message.cancelled`, `message.filtered`, `message.blocked` | No equivalent states. Use the HTTP response and `command.result` | different | `messaging/send` |
| `templates.approved`, `templates.rejected`, `templates.paused`, `templates.disabled`, `templates.quality_updated`, `templates.category_updated` | `template.status`, with `kind` for an approval or a quality change | same | `api-events` |
| `contact.opt_out`, `contact.opt_in` (STOP, START and custom keywords) | `contact.opted_out`, `contact.opted_in` for keyword replies to campaign messages | different | `campaigns/opt-outs` |
| `contact.help` and the HELP auto-reply | Not offered | gap | none |
| `channel.*` events | No equivalent. Read the Connection with `connection.status` and the other connection events | different | `connections/manage` |
| `link.clicked`, `link.expired` | `campaign.recipient_link_opened` for campaign links | different | `campaigns/link-tracking` |
| Inbound media | No hosted copy. Download from the message (`GET /messaging/media/{id}`) or `POST /messaging/media/{id}/download-and-save` to your own storage | different | `messaging/media` |
| `GET /v3/conversations` | Read history through the history endpoints of the Messaging API | different | `messaging/history` |

### 1.5 Contacts and opt-outs

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Contacts created at the first message, with an opt-out flag that applies on every channel | A team-wide opt-out list that campaigns respect: `POST /platform/optouts`, `POST /platform/optouts/batch` (up to 1,000 phone numbers), `GET /platform/optouts` | different | `campaigns/opt-outs` |
| Contact list and attributes | Audiences, segments and audience profiles for campaigns | different | `campaigns/audiences` |

### 1.6 Groups, channels and calls

| Sent | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| WhatsApp groups and channels (not in Sent's documentation) | Group operations and channels on linked-device Connections | more | `messaging/contacts-and-groups`, `messaging/channels` |
| Phone calls from your numbers, with browser and mobile voice SDKs, recordings and voice agents | WhatsApp calls: `POST /messaging/voip/calls`, browser call components with client tokens, and SIP trunks. Polymorfa does not record calls | different | `calls/server`, `calls/web`, `calls/sip-trunks` |
| `call.initiated`, `call.answered`, `call.completed`, `call.failed`, `call.recording_ready` | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended`, `call.telemetry` and the other call events. No recording event | different | `calls/how-calls-work`, `api-events` |

## 2. Webhooks

| Item | Sent | Polymorfa |
| --- | --- | --- |
| Registration | Dashboard or API, with a `whsec_` signing secret | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` or `meta`) |
| Body | JSON with `field`, `event`, `timestamp`, `payload` | Native envelope: `{"id", "connection", "timestamp", "event", "payload"}`, or Meta's `object`/`entry`/`changes` envelope |
| Signature | Version 2: `webhook-id`, `webhook-timestamp` and `webhook-signature` (`v1,{base64}`), HMAC-SHA256 over `{id}.{timestamp}.{raw_body}`, 5-minute tolerance. Version 1: `X-Webhook-*` headers | `native`: `X-Webhook-Signature`; `meta`: `X-Hub-Signature-256: sha256=<hex>`. HMAC-SHA256 over the exact raw body with the endpoint's signing secret |
| Retries | Version 2: 5 attempts over about 2.6 hours, timeout 5 to 120 seconds, replay from the dashboard | Up to 8 attempts over 24 hours, on network error, timeout, `408`, `429` and `5xx`. Respond with 2xx within 30 seconds after saving the event |
| Redelivery | Dashboard replay | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |

Dedupe on the envelope `id`. Delivery is at least once and unordered. See `development/webhooks`.

## 3. Behaviour differences a migrating agent must handle

1. **WhatsApp only.** Leave SMS, MMS and RCS sends, and the `channel` and `channels` fields, with the user's Sent code. Move only the WhatsApp part, and agree with the user where the code chooses between channels.
2. **Templates do not carry over.** Sent template ids, slugs and names belong to Sent. List each one with the user, then recreate it as a project template or on the WABA with the Graph API. Meta approves it again for the sending account.
3. **The WABA.** Sent holds the access token of the WABA the customer connected, and a number belongs to one WABA at a time. Ask the user whether the WABA moves or stays, and to confirm it with Meta and Sent before any Connection is created. Do not assume a template or number can be shared by two providers.
4. **Cloud API access.** Meta Cloud API onboarding is in beta and needs team access. If the team lacks it, tell the user; do not hide the choice behind a linked-device Connection.
5. **Batches and scheduling.** A Sent send takes up to 1,000 recipients and an optional `scheduled_at`. A Polymorfa send has one recipient. List each use and agree whether code loops over recipients or a campaign takes the send.
6. **Sender profiles.** Map each profile to a Customer and its Connection. Do not copy a profile's Sent sender or SMS settings.
7. **Status states.** Polymorfa has no `queued`, `routed`, `scheduled`, `filtered` or `blocked` states. Treat a successful send response as accepted and read `message.ack`.
8. **Opt-outs.** Sent stores an opt-out as a flag on the contact for every channel. Export the opted-out contacts and import them into the Polymorfa opt-out list with the batch route. Polymorfa captures STOP and START only for replies to campaign messages.
9. **Idempotency.** Sent keeps a key for 24 hours and Polymorfa for 1 hour. Retry within the hour with the same `Idempotency-Key`, or keep your own record for a longer window.
10. **Phone formats.** Graph `to` has no plus sign; the Messaging API takes E.164. Normalise once at the adapter.
11. **Media.** Download media when the event arrives. Polymorfa keeps no copy of received attachments.
12. **Linked-device limits.** Outside Campaigns a linked-device Connection cannot start a chat with someone who never wrote to it (`bansafe_cold_blocked`), and sends are paced. Sent's official-route sends are not subject to this. Tell the user before moving outreach.
13. **Disconnected Connections.** A send to a disconnected Connection fails with `503 connection_not_ready`. Keep your own outbox and retry with the same `Idempotency-Key`.
14. **Billing.** Sent charges $0.015 for each person messaged in a calendar month plus message costs at destination rates. Polymorfa charges linked-device Connections per online day by tier; on Meta Cloud API Connections Meta bills the business's WABA directly. See `billing/connection-tiers`.
15. **Async completion.** Restart and logout return `202` plus an operation id. Wait for `connection.status` before the next step.
