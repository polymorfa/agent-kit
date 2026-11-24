# Gupshup reference for polymorfa-migrate

Maps Gupshup's WhatsApp Self Serve API (https://docs.gupshup.io) to Polymorfa. Checked on 24 November 2026 against Gupshup's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/gupshup.

## Requests and credentials

Gupshup: form-encoded `POST https://api.gupshup.io/wa/api/v1/msg` (session messages) and `POST https://api.gupshup.io/wa/api/v1/template/msg` (templates), with an `apikey` header. Fields are `channel`, `source`, `destination`, `src.name` and `message`, where `message` is a JSON string. The response is `{"status":"submitted","messageId":"..."}`; delivery is reported on the callback URL. Gupshup refuses calls made directly from a browser. It is replacing API keys with short-lived Customer App Tokens and stops accepting keys on 31 March 2027; apps linked to a Gupshup partner use a Universal Token.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API; use a client token only on native Messaging API paths from a browser. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask the user who owns each WhatsApp Business Account and which Gupshup apps to move before planning. A number registered to Cloud API with Gupshup keeps its registration and two-step verification PIN; the user resolves it with Gupshup first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Gupshup capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| App (Gupshup number) | Connection, created through a QuickLink with Meta Embedded Signup | different | `connections/cloud-api-setup`, `connections/quicklink` |
| Embedded Sign-up | Same QuickLink flow | same | `connections/cloud-api-setup` |
| Coexistence (Coex) | Embedded Signup option to keep using the WhatsApp Business app | same | `connections/cloud-api-setup` |
| Partner Portal and Partner API | Customers API with pairing links for each customer | same | `customers` |
| Wallet that funds Meta's fees | Not offered. Meta bills the user's own WhatsApp Business Account directly | different | `connections/cloud-api-setup` |
| WABA Health | `GET /platform/connections/{connectionId}` and the `connection.status` event; readiness checks run at setup | same | `connections/manage` |
| Session messages: text, image, document, audio, video, sticker, reaction, location | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| List, quick reply and CTA URL messages | Same endpoint, interactive body | same | `messaging/send` |
| Single product, multi-product and catalog messages | Same endpoint, interactive product body; `/{waba-id}/product_catalogs` | same | `api/graph/index` |
| Address messages | Same endpoint, interactive address body | same | `messaging/send` |
| Template send by template ID and `params` | Same endpoint with `type: "template"`, the template `name` and `language`, and Meta's `components` | different | `messaging/templates` |
| Templates created in the dashboard | `POST`, `GET`, `DELETE /{waba-id}/message_templates`; project templates also have preview and submit | more | `messaging/templates` |
| MM Lite messages (v3) | `/{phone-number-id}/marketing_messages`, `/{waba-id}/marketing_messages/status` | same | `api/graph/index` |
| Welcome messages, ice breakers, commands | `/{phone-number-id}/conversational_automation` | same | `api/graph/index` |
| Business profile (details, about, photo) | `/{phone-number-id}/whatsapp_business_profile` | same | `connections/business-profile` |
| Block, unblock, list blocked users | `/{phone-number-id}/block_users` | same | `api/graph/index` |
| Opt-in and opt-out users | Team-wide opt-out list with STOP and START replies, enforced on campaigns. No opt-in record for template sends | different | `campaigns/opt-outs` |
| Media sent by link | Link, or upload with `POST /{phone-number-id}/media` | same | `messaging/media` |
| Stored media | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Business-initiated voice calls over SIP | Calls in the browser, from server code and over SIP, both directions; Graph `/calls` takes Meta's actions | more | `calls/server`, `calls/sip-trunks` |
| Sandbox (charged to the wallet) | Test connections on a simulated network, at 0 credits | more | `testing` |
| Bot Studio journeys and AI agents | Not offered. Connect the user's own agent through the hosted MCP server or the API | gap | `development/mcp` |
| CRM apps (Zoho, HubSpot, Salesforce and others) | Not offered | gap | none |
| Message history | Beta that needs enrollment and hosted message storage | different | `messaging/history` |

Cloud API calls are one-to-one audio. Polymorfa does not record calls.

## Webhooks

Gupshup posts one callback URL per app. Every payload has `app`, `timestamp`, `version` (2) and `type`. Gupshup expects a `2xx` with an empty body within 10 seconds, retries "after a brief interval", and documents IP allowlisting (requested from support) instead of a payload signature. Inbound events are delivered with a 5-second delay.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Gupshup `type` | Polymorfa | Status |
| --- | --- | --- |
| `message` (text, image, file, audio, video, contact, location, button_reply, list_reply) | `message.received`, or Meta `messages` in the meta format; match replies on `replyChoice.id` | same |
| `message-event` `sent`, `delivered`, `read` | `message.ack` | same |
| `message-event` `failed` | `message.failed` (`error` class and `code`) | same |
| `message-event` `enqueued` | The send response carries the message `status` | different |
| `message-event` `deleted` | `message.update`. Check its payload before relying on it | not verified |
| `template-event` (approved, rejected, paused, category and quality updates) | `template.status` | same |
| User events `opted-in`, `opted-out`, `sandbox-start` | `contact.opted_in` and `contact.opted_out` cover STOP and START replies to campaigns only. No `sandbox-start` counterpart | different |
| `billing-event` | Not offered. Meta bills a Cloud API Connection's account directly | gap |
| Account system events (tier, status, capability, review) | Not verified. Check the webhook docs before relying on them | not verified |

Gupshup message ids: `messageId` (API response) and `gsId` are Gupshup's. The event `id` is a Gupshup ID on `enqueued` and `failed`, and a WhatsApp message ID on `sent`, `delivered` and `read`. Gupshup drops `gsId` from events that arrive more than a week after the send. Polymorfa receipts match on the Polymorfa message ID, scoped to the Connection that emitted the event.

## Differences to agree with the user

- Gupshup's form-encoded send changes once to Meta's JSON body. Rewrite sends, then follow Meta's documentation.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- Gupshup refuses a template to a user who has not opted in and a send to a user who opted out (error codes 1006 and 1012). Polymorfa does not keep an opt-in record for template sends, and enforces its opt-out list on campaigns.
- Free-form sends more than 24 hours after the customer's last message fail with `conversation_window_closed`; send a template. Gupshup applies the same rule.
- Template IDs are Gupshup's. Look up each template's name and language, and confirm which WhatsApp Business Account owns it before planning its approval.
- Gupshup message ids and app names do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Download received media when the event arrives; upload outgoing media again.
- Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account. Gupshup bills them through its wallet.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Gupshup one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Close the Gupshup app only after the number runs on Polymorfa. Gupshup deletes an app unused for 60 days.
