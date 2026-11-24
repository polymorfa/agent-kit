# Vonage reference for polymorfa-migrate

Maps Vonage (https://developer.vonage.com/en/messages/overview) to Polymorfa. Checked on 24 November 2026 against Vonage's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/vonage.

## Requests and credentials

Vonage: `POST https://api.nexmo.com/v1/messages` with `to`, `from`, `channel: "whatsapp"` and `message_type`. Phone numbers carry no leading `+` or `00`. The credential is an application JWT in `Authorization: Bearer` (RS256), or basic authentication with an API key and secret. A WhatsApp number is an external account linked to an application. Vonage's sandbox uses `https://messages-sandbox.nexmo.com/v1/messages`.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask the user who owns each WhatsApp Business Account before planning the move. A number registered to Cloud API with Vonage keeps Vonage's registration PIN; the user resolves it with Vonage first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Vonage capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Embedded Sign-Up in the Vonage Dashboard | Connection created through a QuickLink with Meta Embedded Signup | same | `connections/cloud-api-setup`, `connections/quicklink` |
| WhatsApp number linked to an application (External Accounts API) | Connection, addressed by its phone number ID | different | `connections/cloud-api-setup` |
| Hosted Embedded Sign-up for partners (Channel Manager API) | QuickLink, or a Customer with pairing links and a monthly cap | more | `connections/quicklink`, `customers` |
| Coexistence with the WhatsApp Business app (Vonage: not yet supported) | Embedded Signup option to keep using the WhatsApp Business app | more | `connections/cloud-api-setup` |
| Messages API `text`, `image`, `audio`, `video`, `file` | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| Location, contact and reaction messages | Same endpoint | same | `messaging/send` |
| List messages, reply buttons | Same endpoint, interactive body | same | `messaging/send` |
| Carousel messages | Carousel through an approved template on Cloud API. Free-form carousels exist on linked-device Connections | different | `messaging/send` |
| Product messages | Not verified. Check the catalog guide and the Graph API reference before relying on it | not verified | `connections/catalog` |
| Stickers (URL, .webp, 512x512) | `sticker` media object on the messages endpoint, by `link` or uploaded id | same | `messaging/send` |
| Template message | Same endpoint with `type: "template"` | same | `messaging/templates` |
| Template Management API: list, create, delete | `GET`, `POST`, `DELETE /{waba-id}/message_templates`; project templates also have preview and update | more | `messaging/templates` |
| Template Management API: update | Not offered on the Graph API | gap | `messaging/templates` |
| Upload media for template creation and for sending | `POST /{app-id}/uploads` and `POST /{phone-number-id}/media` | same | `messaging/media` |
| Template analytics (Channel Manager API) | Not offered | gap | none |
| Inbound media | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| Other channels (SMS, MMS, RCS, Messenger, Viber, Email) and Dispatch failover | Not offered. Polymorfa sends WhatsApp only | gap | none |
| Messages API Sandbox (100 messages a month, allow-listed numbers) | Test connections on a simulated WhatsApp network at 0 credits | more | `testing` |
| Vonage CLI | Polymorfa CLI, with a local MCP server | more | `get-started/development-environment` |
| Vonage MCP servers (documentation, API bindings) | Hosted MCP server, docs MCP server | same | `development/mcp` |

WhatsApp calling on Vonage was not mapped: Vonage's developer documentation has no WhatsApp calling reference. If the project places or answers WhatsApp calls through Vonage, ask the user and read `calls/server`.

## Webhooks

Vonage sends two webhooks, Inbound Message and Message Status, to the URLs set on the application's Messages capability. Each request carries a JWT in `Authorization: Bearer`, signed with HS256 and the account signature secret. The `payload_hash` claim equals the SHA-256 hash of the body, and `iat` is the issue time. Vonage retries a response that is not 2xx.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Vonage | Polymorfa | Status |
| --- | --- | --- |
| Inbound Message webhook | `message.received`, or Meta `messages` in the meta format | same |
| Message Status webhook (accepted, delivered, rejected) | `message.ack`, `message.failed` | same |
| JWT check with the signature secret | HMAC-SHA256 check with the webhook secret | different |

## Differences to agree with the user

- Vonage requests change once to Meta's shape. Rewrite sends, then follow Meta's documentation.
- Add an `Idempotency-Key` header to Messaging API sends. The Graph API follows Meta's shape.
- Vonage `message_uuid` values, application ids and template ids do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Vonage says it keeps each partner's templates in a separate Messaging Account. Check that each template the project sends is approved for the account connected to Polymorfa, and create the ones that are not.
- Download received media when the event arrives.
- Vonage's platform fee ends with the Vonage account. Meta's message charges for Cloud API Connections stay with the user's WhatsApp Business Account.
- Code that uses other Vonage channels or failover has no Polymorfa equivalent.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Vonage one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Remove the number from the Vonage application only after it runs on Polymorfa.
