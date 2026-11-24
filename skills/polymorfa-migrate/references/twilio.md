# Twilio reference for polymorfa-migrate

Maps Twilio WhatsApp (https://www.twilio.com/docs/whatsapp, Programmable Messaging) to Polymorfa. Checked on 24 November 2026 against Twilio's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/twilio.

Twilio sends WhatsApp messages from official senders on a WhatsApp Business Account (WABA), through the same Messages resource it uses for SMS. It bills $0.005 per WhatsApp message in either direction and passes Meta's per-template fees through. Polymorfa runs the official route as Meta Cloud API Connections (beta, needs team access) and adds linked-device Connections.

## 1. Mapping

### 1.1 Credentials and conventions

| Twilio | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/...`, Basic authentication with the Account SID and auth token (or an API key) | `https://api.polymorfa.com/graph/whatsapp/v26.0/...` or `/messaging/{connection}/...`, `Authorization: Bearer <credential>`. Create keys in the Console | different | `api/authentication` |
| Form-encoded requests and webhooks (`application/x-www-form-urlencoded`) | JSON requests and webhooks | different | `api/overview` |
| `whatsapp:+15551234567` in `To` and `From` | Graph `to`: digits without a plus sign. Messaging API `conversation.phoneNumber`: E.164 with a plus sign. Keep the returned `conversation.id` | different | `messaging/ids` |
| SIDs: `SM...` and `MM...` messages, `MG...` Messaging Services, `HX...` content templates, `AC...` accounts | Opaque string ids. None carry over; look them up again | different | `messaging/ids` |

### 1.2 Senders and onboarding

| Twilio | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| WhatsApp sender registered by self sign-up on the team's own WABA | A Meta Cloud API Connection: create a QuickLink with `connectionPreference` `cloud`; the business completes Embedded Signup. Needs team access. Polymorfa runs readiness checks before the Connection starts | same | `connections/cloud-api-setup`, `connections/quicklink` |
| Number in use in the WhatsApp app, which Twilio asks to delete before registration | A linked-device Connection (QR or pairing code) keeps the app working. Coexistence on Meta Cloud API keeps the Business app in use (beta) | more | `connections/index`, `connections/cloud-api-setup` |
| Tech Provider program with your own Embedded Signup for customers | QuickLink hosted page, optionally branded; Customers API with pairing links and a monthly cap per customer | more | `connections/quicklink`, `customers/index`, `customers/pairing-links` |
| Several senders in a Messaging Service sender pool | No pool. A request names its Connection. Spread traffic in your code or use Campaigns | gap | `campaigns/send` |
| Sandbox for WhatsApp (shared number, join code, 3-day sessions) | Test connections on a simulated network, 0 credits | different | `testing/test-connections` |
| One WABA per Twilio account, subaccount or project | A project can hold many Connections | different | `connections/index` |

Pairing and Embedded Signup are done by a person. An agent cannot complete them. Whether the WABA and its templates move away from Twilio is a decision for the user with Meta and Twilio; do not assume it.

### 1.3 Sending

| Twilio | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `POST .../Messages.json` with `To`, `From`, `Body` | Graph `POST /graph/whatsapp/v26.0/{phoneNumberId}/messages` with `messaging_product: "whatsapp"`, `to`, `type: "text"`, `text.body`; or `POST /messaging/{connection}/messages/send` with `content.text` | same | `api/graph/index`, `messaging/send` |
| `MediaUrl` (images, audio, PDF; 16 MB per message) | `content.image`, `video`, `voice`, `file` with `url` or `base64` | same | `messaging/send`, `messaging/media` |
| `ContentSid` and `ContentVariables` | `content.template` with `name`, `language`, `components`. The template must be approved in that language or the send fails with `template_not_approved` | different | `messaging/templates` |
| Content Template Builder, WhatsApp approval | Project templates: create, preview, submit (`templates:manage`); or the Graph API `/{wabaId}/message_templates` | same | `messaging/templates` |
| Quick reply, call to action | `content.buttons` (`reply`, `url`, and more on linked-device Connections). Cloud API direct sends accept 1 to 3 reply buttons; richer buttons need an approved template | same | `messaging/send` |
| List picker | `content.list` | same | `messaging/send` |
| Card, carousel | `content.carousel` on linked-device Connections; a template on Cloud API | same | `messaging/send` |
| Location | `content.location` | same | `messaging/send` |
| `twilio/flows` | `content.flow`, drafts under `/platform/flows` | same | `messaging/flows` |
| `whatsapp/authentication` templates (copy code) | An authentication template on Cloud API through `content.template` | same | `messaging/templates` |
| `twilio/catalog` | `content.product` and `content.productList` for Business app Connections | different | `connections/catalog` |
| `twilio/pay` | No equivalent found | gap | none |
| `ScheduleType=fixed` and `SendAt` (Messaging Service only) | Campaigns with `scheduledAt` and `throughput.ratePerMinute` | different | `campaigns/send` |
| `ValidityPeriod` | Not offered | gap | none |
| Link tracking | Campaign link tracking | different | `campaigns/link-tracking` |
| Idempotency (not documented on Twilio) | `Idempotency-Key` header, 1-hour receipt | more | `development/idempotency` |
| `Prefer: respond-async` (not on Twilio) | Returns `202`, with the result as `command.result` | more | `messaging/send` |

Cloud API Connections follow Meta's rules, as on Twilio: a free-form message outside the 24-hour customer service window fails with `conversation_window_closed`; send an approved template.

### 1.4 Receiving and status

| Twilio | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Inbound webhook fields `MessageSid`, `From`, `To`, `Body`, `NumMedia`, `MediaUrl0` | `message.received`: `payload.id`, `payload.conversation`, `payload.type` and the text or media fields | same | `messaging/receive` |
| `ProfileName`, `WaId` | `payload.pushName`; `conversation.phoneNumber` and `conversation.id` when WhatsApp reveals them | same | `messaging/user-identities` |
| `ButtonPayload`, `ButtonText`, `ButtonType` | `message.received` type `button_reply`, `list_reply` or `native_flow_response`; match on `replyChoice.id` | same | `messaging/receive` |
| `Latitude`, `Longitude`, `Address`, `Label` | `message.received` type `location` | same | `messaging/receive` |
| `FlowData` | `native_flow_response` | same | `messaging/receive` |
| `Forwarded`, `FrequentlyForwarded` | Not found on the payload | gap | none |
| `Referral*` fields (Click-to-WhatsApp) | The `referral` object on Cloud API messages: an entry point, not a conversion | same | `development/webhooks` |
| `OriginalRepliedMessageSid` | `payload.parentMessageId` | same | `messaging/receive` |
| StatusCallback `MessageStatus` `sent` | `message.sent` | same | `api-events` |
| `delivered`, `read` | `message.ack` type `delivered`, `read` (and `played`) | same | `api-events` |
| `failed`, `undelivered`, `ErrorCode` | `message.failed`, or `message.ack` type `error`; synchronous errors return an HTTP error with a stable `error.code` | different | `api/errors` |
| `queued`, `sending`, `scheduled`, `canceled` | No equivalent states. Use the HTTP response and `command.result` | different | `messaging/send` |
| Inbound media at `MediaUrl{N}`, Basic authentication, kept until deleted | No hosted copy. Download from the message (`GET /messaging/media/{id}`) or `POST /messaging/media/{id}/download-and-save` to your own storage | different | `messaging/media` |

### 1.5 Groups and calls

| Twilio | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Group messaging through the Conversations API | Group operations on linked-device Connections: create, members, admins, settings, invites, under `/messaging/{connection}/groups` | same | `messaging/contacts-and-groups` |
| WhatsApp Business Calling into a TwiML Voice application (`<Dial><WhatsApp>`, Calls API) | `POST /messaging/voip/calls`, browser call components with client tokens, and SIP trunks | more | `calls/server`, `calls/web`, `calls/sip-trunks` |
| Call permission requests | `content.callPermissionRequest`, `/platform/call-opt-outs`, call policy, blocked country codes | same | `calls/permissions` |
| Voice application webhooks | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended`, `call.telemetry` and the other call events | more | `calls/how-calls-work`, `api-events` |
| Calls cannot connect to PSTN endpoints | A SIP trunk rings your phone system and calls out from it | more | `calls/sip-trunks` |

## 2. Webhooks

| Item | Twilio | Polymorfa |
| --- | --- | --- |
| Registration | Console URL or `StatusCallback` per message | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` or `meta`) |
| Body | Form-encoded | JSON. Native envelope: `{"id", "connection", "timestamp", "event", "payload"}` |
| Signature | `X-Twilio-Signature`, HMAC-SHA1 of URL and params with the auth token (`bodySHA256` for JSON) | `native`: `X-Webhook-Signature`; `meta`: `X-Hub-Signature-256: sha256=<hex>`. HMAC-SHA256 over the exact raw body with the endpoint's signing secret |
| Retries | `rc` 0 to 5, default 1; default only on TCP or TLS connect failure; 5xx only with `rp`; 15 seconds in total | Up to 8 attempts over 24 hours, on network error, timeout, `408`, `429` and `5xx`. Respond with 2xx within 30 seconds after saving the event |
| Redelivery | None documented | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |

Dedupe on the envelope `id`. Delivery is at least once and unordered. See `development/webhooks`.

## 3. Behaviour differences a migrating agent must handle

1. **Templates do not carry over.** `ContentSid` values belong to Twilio. List each one with the user, then recreate it as a project template or on the WABA with the Graph API. Meta approves it again for the sending account.
2. **The WABA.** Twilio ties one WABA to one Twilio account. Ask the user whether the WABA moves or stays, and to confirm it with Meta and Twilio before any Connection is created. Do not assume a template or number can be shared by two providers.
3. **Cloud API access.** Meta Cloud API onboarding is in beta and needs team access. If the team lacks it, tell the user; do not hide the choice behind a linked-device Connection.
4. **Sender pools and scheduling.** `MessagingServiceSid` pools and `SendAt` have no Polymorfa equivalent outside Campaigns. List each use and agree the replacement.
5. **Status states.** Polymorfa has no `queued` or `sending`. Treat a successful send response as accepted and read `message.ack`.
6. **Phone formats.** Strip `whatsapp:` and normalise once at the adapter. Graph `to` has no plus sign; the Messaging API takes E.164.
7. **Media.** Download media when the event arrives. Twilio media URLs are not Polymorfa media references.
8. **Linked-device limits.** Outside Campaigns a linked-device Connection cannot start a chat with someone who never wrote to it (`bansafe_cold_blocked`), and sends are paced. Twilio senders on the official route are not subject to this. Tell the user before moving outreach.
9. **Disconnected Connections.** A send to a disconnected Connection fails with `503 connection_not_ready`. Keep your own outbox and retry with the same `Idempotency-Key`.
10. **Billing.** Twilio charges $0.005 per message plus Meta's fees. Polymorfa charges linked-device Connections per online day by tier; on Meta Cloud API Connections Meta bills the business's WABA directly. See `billing/connection-tiers`.
11. **Async completion.** Restart and logout return `202` plus an operation id. Wait for `connection.status` before the next step.
