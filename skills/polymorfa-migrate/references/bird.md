# Bird reference for polymorfa-migrate

Maps Bird (https://bird.com/docs/guides/whatsapp/overview, formerly MessageBird) to Polymorfa. Checked on 24 November 2026 against Bird's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/bird.

## Requests and credentials

Bird: `https://us1.platform.bird.com/v1/whatsapp/...` or `https://eu1.platform.bird.com/v1/whatsapp/...`, the region set by the key (`bk_us1_...`, `bk_eu1_...`). `Authorization: Bearer <workspace API key>`. Key permissions are scope and level pairs such as `whatsapp` (send) and `whatsapp_management` (templates, settings, numbers). A key belongs to one workspace. Billing operations cannot be granted to a workspace key.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`.

Ask the user who owns each WhatsApp Business Account before planning the move. Bird connects a number only from its dashboard or CLI, so the user may hold the Meta login. A number registered to Cloud API with another provider keeps that provider's registration PIN; the user resolves it with Bird first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Bird capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Number connected in Meta's Embedded Signup from the dashboard or CLI | Connection created through a QuickLink from your code, with Embedded Signup for Cloud API | more | `connections/cloud-api-setup`, `connections/quicklink` |
| Coexistence for a WhatsApp Business app number | Embedded Signup option to keep using the WhatsApp Business app, or a linked-device Connection paired with the app running | more | `connections/cloud-api-setup`, `connections/quicklink` |
| Default numbers for `bird_` templates | Not offered. Every send comes from a Connection the user owns | gap | none |
| Number status and number events | `GET /platform/connections/{connectionId}` and the `connection.status` event | same | `connections/manage` |
| `POST /v1/whatsapp/messages` with `to`, `from` | `POST /{phone-number-id}/messages` with Meta's body | same | `messaging/send` |
| `text`, `image`, `video`, `audio`, `sticker`, `document`, `location`, `contact_cards` | The same message types in Meta's body | same | `messaging/send` |
| `interactive`: reply buttons, list menus, CTA URL buttons, carousels | Same endpoint, interactive body. Linked-device Connections also send buttons, lists, carousels and polls through the Messaging API | more | `messaging/send` |
| `template.slug`, `language`, named `parameters` or Meta `components` | `type: "template"` with the template name, language and `components` | same | `messaging/templates` |
| Templates: create, version, languages, submit | `POST`, `GET`, `DELETE /{waba-id}/message_templates`; project templates also have preview and submit | same | `messaging/templates` |
| Bird-managed templates (slug starts with `bird_`) | Not offered. Recreate on the user's own WhatsApp Business Account | gap | `messaging/templates` |
| `in_reply_to_message_id` | `context.message_id` | same | `messaging/send` |
| `tags` (up to 20), `reference`, `metadata` (up to 2 KB) | No field in Meta's body. Keep in the user's own store by message `id`. Connection `externalId` on a QuickLink covers per-number references | different | `connections/quicklink` |
| One recipient per request, no batch endpoint | Same. Bulk sending is Campaigns, on Pro Connections | same | `campaigns` |
| `to` as a phone number or a business-scoped user ID (BSUID) | Phone number in Meta's body. User IDs carry phone number, BSUID and username as optional aliases | different | `messaging/user-identities` |
| `POST /messages/{id}/read` with `typing_indicator` | `status: "read"` on Cloud API Connections; mark seen and typing through the Messaging API on linked devices | same | `messaging/send` |
| `PUT` and `DELETE /messages/{id}/reaction` | `reaction` message, or `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| Inbound media fetched with `GET /messages/{id}/media/{media_id}`, kept 30 days | Polymorfa keeps no file. Download from the message, or `POST /messaging/media/{id}/download-and-save` to the user's storage | different | `messaging/media` |
| `GET /messages` and `GET /conversations/{id}/messages` (30 days) | Message history, a beta that needs enrollment and hosted message storage | different | `messaging/history` |
| Conversations: assignee, labels, take over from an AI agent | Not offered | gap | none |
| Groups (Official Business Account only, 8 participants) | Groups on linked-device Connections under `/messaging/{connection}/groups`. The Graph API has no group operations | different | `messaging/contacts-and-groups` |
| Group join requests: list, approve, reject | Not offered | gap | none |
| Broadcasts: one template to an audience | Campaigns and audiences, on Pro Connections | more | `campaigns` |
| Suppressions | Team-wide opt-out list: `POST /platform/optouts`, CSV import, STOP and START replies captured | different | `campaigns/opt-outs` |
| Preferences (all or non-transactional) and keyword rules | Not offered | gap | none |
| Statistics by country, template, category, error code, tag, number | Not offered. Connection analytics cover engagement for linked-device Connections | gap | `connections/analytics` |
| Send API rate limits by plan | `429` with `Retry-After`; respect it | same | `api/rate-limits` |
| Hosted MCP server (curated tools) | Hosted MCP server with 200+ tools, and a local MCP in the CLI | more | `development/mcp` |
| CLI with `bird webhooks` | Polymorfa CLI with a command for every resource and webhook events forwarded to localhost | more | `development/cli` |

## Calls

Bird's API has no WhatsApp call operation. Its `/v1/voice` API places phone-network calls with sequences and SIP trunks, and its WhatsApp calling guide is a planning checklist that says WhatsApp calling must not be bridged to the public telephone network.

| Bird capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Voice API calls and SIP trunks on the phone network | Not a replacement. Polymorfa Calls carry WhatsApp calls in the browser, from server code and over SIP | different | `calls/how-calls-work`, `calls/sip-trunks` |

Cloud API calls are one-to-one audio. Polymorfa does not record calls.

## Webhooks

Bird: `POST /v1/webhooks` (or `bird webhooks create`). Each delivery has the header `webhook-signature: v1,<base64 HMAC-SHA256>` over the webhook ID, the `webhook-timestamp` and the raw body, keyed with the endpoint secret (`whsec_...`, base64-decoded). Eight attempts over about 27.5 hours, 15 seconds to respond, replays limited to 20 per organization per UTC day. Envelope: `type`, `timestamp`, `data`.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex, with no timestamp in the signed string. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Bird event | Polymorfa | Status |
| --- | --- | --- |
| `whatsapp.received` (carries the content) | `message.received`, or Meta `messages` in the meta format | same |
| `whatsapp.accepted` | The send response; `status` reports that WhatsApp accepted the message | different |
| `whatsapp.sent` | `message.sent` | same |
| `whatsapp.delivered`, `whatsapp.read` | `message.ack` | same |
| `whatsapp.failed` | `message.failed` | same |
| `whatsapp.rejected` (wallet, price or suppression) | Not offered. The send call refuses instead | gap |
| `whatsapp.reacted` | `message.reaction` | same |
| `whatsapp_suppression.created` | Not offered | gap |
| `whatsapp.group.join_request_created`, `whatsapp.group.join_request_revoked` | Not offered | gap |

## Differences to agree with the user

- Bird's request shape changes once to Meta's. Rewrite sends, then follow Meta's documentation.
- Replace the Bird signature check (id, timestamp and body, base64) with Polymorfa's raw-body check. Drop the timestamp tolerance logic unless the user wants to keep their own.
- Add an `Idempotency-Key` header to Messaging API sends; Polymorfa keeps it for 1 hour, Bird for 3. The Graph API follows Meta's shape.
- Bird bills its own fee per outbound message from a prepaid wallet and may end a send as `rejected` with `insufficient_balance` or `price_not_found`. Polymorfa has no per-message fee on linked-device Connections, and Meta bills the user's WhatsApp Business Account directly for Cloud API messages. Find code that reads `cost`, 402 wallet errors or the `rejected` status.
- Bird refuses a free-form send outside the 24-hour window with a 422. Cloud API Connections follow Meta's window and template rules. Outside Campaigns, a linked-device Connection cannot start a chat with someone who never wrote to it.
- Bird ids (`wam_`, `waf_`, `wag_`, `ws_`, template slugs, BSUIDs) do not carry over. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Download received media when the event arrives; upload outgoing media again.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Bird one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Close the Bird number only after it runs on Polymorfa.
