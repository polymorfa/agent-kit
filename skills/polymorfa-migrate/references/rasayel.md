# Rasayel reference for polymorfa-migrate

Maps Rasayel (https://developers.rasayel.io) to Polymorfa. Checked on 24 November 2026 against Rasayel's published pricing page and developer documentation, and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/rasayel.

## What Rasayel is

Rasayel is a team inbox for WhatsApp sales teams with a public GraphQL API. Its numbers run on the WhatsApp Business Platform. Polymorfa has no inbox product, so the migration covers what the user's code calls. Conversation state, assignment, tags, notes and the chatbot builder stay in Rasayel or move to code the user owns.

## Requests and credentials

Rasayel: GraphQL. API keys come from Rasayel's API management page and go in the `Authorization` header. A key is read-only (queries) or read-write (queries and mutations). Lists use cursor pagination with `PageInfo` and `endCursor`. Limits on the GraphQL API are a leaky bucket of 1,000 complexity points a minute per app on Start (the pricing page lists 1,500 on Grow and 2,000 on Enterprise); most queries cost 0 or 1 point and mutations usually 10 or 20. A response carries `extensions` with `currentlyAvailable`, `restoreRate` and `maximumAvailable`, and an exceeded limit returns an error with `retryAfter`. The pricing page lists a REST API at 100 requests a minute on Start. Rasayel's developer docs describe only the GraphQL API.

Polymorfa: Graph API at `https://api.polymorfa.com/graph/whatsapp/v26.0/{phone-number-id}/...` with `Authorization: Bearer <project token or team key>`. Request and error shapes follow Meta's. Client tokens and Test keys are refused on the Graph API. Native Messaging API paths start with `https://api.polymorfa.com/messaging/{connection}`. Every limited response carries `X-RateLimit-*` headers, and a `429` carries `Retry-After`.

Ask the user who owns each WhatsApp Business Account before planning the move, and whether Rasayel registered the number. A number registered to Cloud API with another provider keeps that provider's registration PIN; the user resolves it with Rasayel first. Polymorfa Cloud API onboarding is a beta that needs team access.

## Mapping

| Rasayel capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| WhatsApp number connected in the inbox (3 on Start, 5 on Grow) | Connection created through a QuickLink, with Embedded Signup for Cloud API | more | `connections/cloud-api-setup`, `connections/quicklink` |
| Extra number at $20 a month | No seats. Each Connection is billed for the days it is online | different | `billing/usage` |
| `textMessageCreate` (input `conversationId`, `body`, `replyToMessageId`) | `POST /{phone-number-id}/messages` with Meta's body, `context.message_id` for a reply | same | `messaging/send` |
| `textProactiveMessageCreate` (input `channelId`, `receiver`, `body`) | The same endpoint addressed to a phone number | same | `messaging/send` |
| `mediaMessageCreate` (input `blobOrAttachmentId`), `attachmentUpload`, `attachmentUploadFromUrl` | The same endpoint with an `image`, `video`, `audio` or `document` body, by `link` or uploaded id | same | `messaging/send`, `messaging/media` |
| `richMessageCreate` with interactive buttons and quick replies | Same endpoint, interactive body. Linked-device Connections also send buttons, lists, carousels and polls through the Messaging API | more | `messaging/send` |
| `templateMessageCreate`, `templateProactiveMessageCreate` (input `messageTemplateId`, `components`) | `type: "template"` with the template name, language and `components` | same | `messaging/templates` |
| `templateSubmit`, `templateUpdate`, `templateSetActive`, `templateDelete`, `templatesSync` | `POST`, `GET`, `DELETE /{waba-id}/message_templates`; project templates also have preview and submit | same | `messaging/templates` |
| WhatsApp Flows forms and flow response events | Flow builder in the Console, `flow_id` in a send, response in the incoming message payload | same | `messaging/flows` |
| `messageRetrySend`, `messageDelete` | Send again with the same `Idempotency-Key`; delete a message on a linked-device Connection | different | `development/idempotency` |
| `noteMessageCreate` (internal note) | Not offered | gap | none |
| `gifMessageCreate` | Not verified. Check the send guide before relying on it | not verified | `messaging/send` |
| Contacts (`channelUserCreate`, `channelUserUpdate`, properties, `dataAttributeCreate`) | Not offered as CRM fields. Audiences and segments for campaigns; chat labels on linked devices | different | `campaigns/audiences`, `messaging/contacts-and-groups` |
| Tags (`channelUserTag`, `conversationTag`) | Chat labels on a linked-device Connection | different | `messaging/contacts-and-groups` |
| Conversation state and assignment (`conversationOpen`, `conversationClose`, `conversationSnooze`, `conversationAssign`, `conversationTeamAssign`, `conversationSetState`) | Not offered | gap | none |
| Chatbot builder (`workflowBotSend`, `workflowBotSendProactive`) | Not offered. Write the logic in code, or connect an agent over MCP | different | `development/mcp` |
| Broadcasts (250 users a day on Start, 5K on Grow, 10K on Enterprise) | Campaigns and audiences, on Pro Connections | more | `campaigns` |
| Opt-in management (listed as Soon) | Team-wide opt-out list: `POST /platform/optouts`, CSV import, STOP and START replies captured | different | `campaigns/opt-outs` |
| WhatsApp Groups (listed as Soon) | Groups on linked-device Connections under `/messaging/{connection}/groups`. The Graph API has no group operations | more | `messaging/contacts-and-groups` |
| Business calling (listed as Soon) | Calls in the browser, from server code and over SIP, in both directions | more | `calls` |
| CRM integrations: Pipedrive, HubSpot, Salesforce | Not offered. Use n8n, Zapier or Make, or your own sync | different | `development/webhooks` |
| Zapier integration | Zapier, n8n and Make integrations | same | none |
| Roles and teams in the inbox | Team roles, scoped keys and audit history | different | `development/api-keys` |
| Reports and insights | Not offered as inbox reports. Connection analytics cover engagement for linked-device Connections | gap | `connections/analytics` |
| Message history in the inbox | Message history, a beta that needs enrollment | different | `messaging/history` |
| Hosted MCP server | Hosted MCP server with 150+ tools, and a local MCP in the CLI | more | `development/mcp` |

## Webhooks

Rasayel: create a subscription with `webhookSubscriptionCreate` (input `url` and `events`), update with `webhookSubscriptionUpdate`, remove with `webhookSubscriptionDestroy`. Rasayel makes an HTTP POST to the endpoint for each subscribed event. The envelope has `event`, `id`, `account`, `app`, `createdAt`, `deliveryAttempts`, `firstDeliveryAttempt` and `data`. The webhook guide documents no signature, no signing secret and no retry schedule. On the pricing page, Start excludes Flows webhooks.

Event types (`WebhookEventTypeEnum`): `CONVERSATION_CREATED`, `CONVERSATION_OPENED`, `CONVERSATION_CLOSED`, `CONVERSATION_SNOOZED`, `CONVERSATION_ASSIGNED`, `CONVERSATION_TAG_CREATED`, `CONVERSATION_TAG_DESTROYED`, `MESSAGE_CREATED`, `MESSAGE_UPDATED`, `MENTION_CREATED`, `CHANNEL_USER_CREATED`, `CHANNEL_USER_TAG_CREATED`, `CHANNEL_USER_TAG_DESTROYED`, `MESSAGE_TEMPLATE_CREATED`, `MESSAGE_TEMPLATE_UPDATED`, `WORKFLOW_BOT_FLOW_STARTED`, `WORKFLOW_BOT_FLOW_FINISHED`, `WHATSAPP_FLOW_RESPONSE_STATE_CREATED`, `CLEO_AGENT_FINISHED`. The `message.created` page says it fires when a message is sent from a channel user.

Polymorfa: create a webhook with `format: "meta"` to receive Meta's `object/entry/changes/value` envelope signed with `X-Hub-Signature-256`, or use native events signed with `X-Webhook-Signature`. Both are HMAC-SHA256 over the raw body in lowercase hex, with no timestamp in the signed string. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Rasayel event | Polymorfa | Status |
| --- | --- | --- |
| `MESSAGE_CREATED` | `message.received`, or Meta `messages` in the meta format | same |
| `MESSAGE_UPDATED` | `message.ack`, `message.failed`, `message.update`. Read the Rasayel payload before mapping each case | different |
| `MESSAGE_TEMPLATE_CREATED`, `MESSAGE_TEMPLATE_UPDATED` | `template.status` | different |
| `WHATSAPP_FLOW_RESPONSE_STATE_CREATED` | `message.received` with the Flow response in its payload | different |
| `CONVERSATION_*`, `MENTION_CREATED`, `CHANNEL_USER_*`, tag events | Not offered. Polymorfa keeps no inbox state | gap |
| `WORKFLOW_BOT_FLOW_STARTED`, `WORKFLOW_BOT_FLOW_FINISHED`, `CLEO_AGENT_FINISHED` | Not offered | gap |

## Differences to agree with the user

- Rasayel owns the inbox state: conversation status, assignment, tags, mentions, notes, properties and chatbot runs. Find every place the code reads or writes them. Agree whether the sales team keeps Rasayel on unmoved numbers, builds on the UI Kit inbox components, or keeps that state in its own store.
- Rasayel ids do not carry over: `conversationId`, `channelId` and `messageTemplateId` are Rasayel integers, and message ids are Rasayel strings. Keep the phone number IDs and WhatsApp Business Account IDs Meta assigned, and look up the rest again.
- Rasayel documents no webhook signature. Add a Polymorfa signature check on the raw body and ignore a repeated event id, because delivery is at least once.
- Remove client-side budgeting of Rasayel complexity points. Respect `Retry-After` on a Polymorfa `429` instead.
- Cloud API Connections follow Meta's 24-hour window and template rules. Outside Campaigns, a linked-device Connection cannot start a chat with someone who never wrote to it.
- Polymorfa keeps no media file. Download received media when the event arrives, and upload outgoing media again.
- Rasayel prices seats, with extra numbers at $20 a month. Polymorfa bills a linked-device Connection for the days it is online, with no seats.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Rasayel one and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. Connect the first number through QuickLink and send a test message.
5. Switch that number's traffic, watch delivery events, then move the next number.
6. Close the Rasayel number only after it runs on Polymorfa.
