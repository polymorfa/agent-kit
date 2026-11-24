# Green API reference for polymorfa-migrate

Maps Green API (https://green-api.com/en/docs/) to Polymorfa. Checked on 24 November 2026 against Green API's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/green-api.

Green API calls every method as `{apiUrl}/waInstance{idInstance}/{method}/{apiTokenInstance}`; file uploads use the `mediaUrl` host. Partner methods use `{partnerApiUrl}/partner/{method}/{partnerToken}`. Polymorfa native paths start with `https://api.polymorfa.com/messaging/{connection}` and Platform paths with `https://api.polymorfa.com/platform`. Users, groups and messages are addressed by opaque decimal ids, never by WhatsApp ids.

## 1. Mapping

### 1.1 Instance lifecycle and pairing

| Green API method | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Create instance (console, or partner `createInstance`) | Create a QuickLink: `POST /messaging/quicklinks`. The Connection exists once the link is created and its id is returned as `data.connection`. Console: Connections > New connection. | different | `connections/quicklink` |
| `QR`, `Scanqrcode` | `GET /messaging/{connection}/pair/qr`: JSON `data.qr`, or `?format=image` for a PNG. Needs direct-pairing access for the team, else `403` pointing to QuickLink. | different | `connections/direct-pairing` |
| `GetAuthorizationCode` (`phoneNumber`, digits only) | `POST /messaging/{connection}/pair/code` with `{"phone":"+15550001111"}`; the code is in `data.code`. Same access gate. QuickLink also shows a pairing code. | same | `connections/direct-pairing`, `connections/quicklink` |
| `GetStateInstance` (`notAuthorized`, `authorized`, `blocked`, `sleepMode`, `starting`, `suspended`) | `GET /platform/connections/{connectionId}`: `status` is `CONNECTING`, `CONNECTED` or `DISCONNECTED`, with `statusReason`. Push events: `connection.status`, `connection.connected`, `connection.logged_out` (`reason`: `banned`, `device_removed`, `unknown`), `connection.restriction_updated`. | more | `connections/manage` |
| `GetStateInstanceHistory` | Not offered as a call. Keep the `connection.status` events you receive. | gap | `connections/manage` |
| `Reboot` | `POST /platform/connections/{connectionId}/restart`. Returns `202` with an `operationId`; poll `GET /platform/operations/{id}` or wait for `connection.status`. | same | `connections/manage` |
| `Logout` | `POST /platform/connections/{connectionId}/logout` unlinks the phone (`202`, async). `POST .../stop` pauses without unlinking. | same | `connections/manage` |
| `SetProfilePicture` | `PUT /messaging/{connection}/profile/picture` (and `DELETE`). | same | `messaging/contacts-and-groups` |
| `GetSettings`, `SetSettings` | No single settings object. Pacing and typing: Safe Mode. Event choice: the webhook's `eventTypes`. Calls: `PUT /platform/connections/{connection}/call-settings`. | different | `safety/safe-mode`, `development/webhooks` |
| `UpdateApiToken` | Rotate or revoke the API key in the Console. There is no per-instance token. | different | `development/api-keys` |
| `GetWaSettings` | `GET /platform/connections/{connectionId}/me` (connected account) and `GET /platform/connections/{connectionId}/capabilities`. | different | `connections/capabilities` |
| Delete instance (partner `deleteInstanceAccount`) | `DELETE /platform/connections/{connectionId}`; bulk `POST /platform/connections/delete` and `POST /platform/connections/stop` (up to 100). | same | `connections/manage` |
| Partner `getInstances`, `createInstance` | Customers API: `POST /platform/customers`, `GET /platform/customers/{id}/connections`, pairing links `POST /platform/customers/{customerId}/pairing-links`, a shared monthly cap per customer. | more | `customers`, `customers/pairing-links` |

### 1.2 Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?, isForwarded?}`. The response has `id`, `whatsapp_ids`, `conversation`, `timestamp`, `type`, `content` and `status`. Graph equivalent: `POST /graph/whatsapp/{version}/{phoneNumberId}/messages` (Meta request shape).

| Green API method | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `sendMessage` (`chatId`, `message`) | `content.text`. `conversation.phoneNumber` is E.164 with `+`. | same | `messaging/send` |
| `quotedMessageId` | `quotedMessage:{id}` (Polymorfa message id). | same | `messaging/send` |
| `linkPreview`, `typePreview`, `customPreview` | No send-side link preview field. Put the URL in `content.text`. | gap | `messaging/media` |
| `typingTime` | Safe Mode `typing`, or `POST /messaging/{connection}/messages/typing` before a send. | different | `safety/safe-mode` |
| `sendFileByUrl`, `sendFileByUpload`, `uploadFile` | `content.image`, `content.video`, `content.voice` (`ptt:true` for a voice note), `content.file` (`url` or `base64`, `caption`, `filename`, `mimeType`). Uploads: `POST /messaging/{connection}/media/uploads`. | same | `messaging/send`, `messaging/media` |
| `sendLocation` | `content.location:{lat,long,address}` | same | `messaging/send` |
| `sendContact` | `content.contact:{vcard}`. A contacts array needs one request per card. | same | `messaging/send` |
| `sendPoll` | `content.poll:{title, options (2-12), multiSelect}` | same | `messaging/send` |
| `sendInteractiveButtons`, `sendInteractiveButtonsReply` | `content.buttons` (`reply`, `url`, `call`, `copy`, `catalog`) and `content.list`. Linked devices: up to 10 controls, up to 3 CTAs. Cloud API: 1 to 3 `reply` buttons only; richer controls need an approved template. Incoming choices arrive as `button_reply`, `list_reply` or `native_flow_response`; match on `replyChoice.id`. | more | `messaging/send`, `messaging/receive` |
| Archived `SendButtons`, `SendTemplateButtons`, `SendListMessage` | Same as above: `content.buttons`, `content.list`. | same | `messaging/send` |
| `forwardMessages` | No forward-by-id call. Send the content again with `isForwarded:true`. | different | `messaging/send` |
| `sendProduct`, `sendOrder`, catalog and collection methods | `content.product`, `content.productList`, `content.order`; `.../business/products`, `.../business/collections`, `.../business/catalog`. Needs a Business App Connection. | more | `connections/catalog` |
| Messages queue (`GetMessagesCount`, `ShowMessagesQueue`, `ClearMessagesQueue`) | No queue. See section 4. | gap | `api/errors` |
| Templates (WABA product) | `content.template` and template CRUD. Cloud API only. | more | `messaging/templates` |
| Idempotency (not documented) | `Idempotency-Key` header, 1-hour receipt. | more | `api/idempotent-requests` |
| Bulk sends | Campaigns: `POST /platform/campaigns`, audiences, opt-outs, A/B. Pro tier. | more | `campaigns` |

### 1.3 Message actions, chats and contacts

| Green API method | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `editMessage` | `PUT /messaging/{connection}/chats/{conversation}/messages/{messageId}` (scope `chats:manage`). Linked device only. | same | `messaging/send` |
| `deleteMessage` | `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` (revoke). | same | `messaging/send` |
| `sendReaction`, `getAllowedReactions` | `POST /messaging/{connection}/messages/react`. | same | `messaging/send` |
| `readChat` | `POST /messaging/{connection}/messages/seen`. | same | `messaging/send` |
| `sendTyping` | `POST /messaging/{connection}/messages/typing` with `state: typing`, `recording` or `paused`. | same | `messaging/send` |
| `archiveChat`, `unarchiveChat` | `POST /messaging/{connection}/chats/{conversation}/archive` and `.../unarchive`. | same | `messaging/linked-device-controls` |
| `setDisappearingChat` | `PUT /messaging/{connection}/chats/{conversation}/disappearing` with `durationSeconds` of 0, 86400, 604800 or 7776000. | same | `messaging/linked-device-controls` |
| `getChats` | `GET /messaging/{connection}/chats`. Needs hosted message storage on for the Connection (beta). | different | `messaging/history` |
| `checkWhatsapp` | `GET /messaging/{connection}/contacts/check?phone=` (a list is accepted). Returns `exists`, `id`, `phoneNumber`. | same | `messaging/user-identities` |
| `getContacts`, `getContactInfo` | `GET /messaging/{connection}/contacts`, `GET .../contacts/{contactId}` and `.../info`. | same | `messaging/user-identities` |
| `getAvatar` | `GET /messaging/{connection}/contacts/{contactId}/picture`. | same | `messaging/user-identities` |
| `addContact`, `editContact`, `deleteContact` | Not offered. | gap | none |
| Journals: `getChatHistory`, `getMessage`, `lastIncomingMessages`, `lastOutgoingMessages` | `GET .../chats/{conversation}/messages` and `.../messages/{messageId}`. Needs hosted message storage (beta), which keeps only type, caption and MIME type, bounded by retention. | different | `messaging/history` |
| `lastIncomingCalls`, `lastOutgoingCalls` | `GET /platform/calls` (call records). | same | `calls/records` |
| Statuses (`sendTextStatus`, `sendVoiceStatus`, `sendMediaStatus`, `deleteStatus`, status statistics and history) | Not offered. | gap | none |

### 1.4 Groups

Group ids are opaque decimals, not `...@g.us`.

| Green API method | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `createGroup` | `POST /messaging/{connection}/groups` with `{name, participants:[user id]}`. Resolve numbers to user ids first with `/contacts/check` or `/identities/resolve`. | same | `messaging/contacts-and-groups` |
| `updateGroupName` | `PUT .../groups/{id}/subject` | same | `messaging/contacts-and-groups` |
| `getGroupData` | `GET .../groups/{id}` (participants included), `GET .../groups/{id}/participants` | same | `messaging/contacts-and-groups` |
| `updateGroupSettings` | Four PUTs: `settings/info-edit`, `settings/messages`, `settings/member-add`, `settings/join-approval` | same | `messaging/linked-device-controls` |
| `addGroupParticipant`, `removeGroupParticipant` | `POST .../groups/{id}/participants/add` and `.../participants/remove` | same | `messaging/contacts-and-groups` |
| `setGroupAdmin`, `removeAdmin` | `POST .../groups/{id}/admin/promote` and `.../admin/demote` | same | `messaging/contacts-and-groups` |
| `setGroupPicture` | `PUT .../groups/{id}/picture` | same | `messaging/contacts-and-groups` |
| `leaveGroup` | `POST .../groups/{id}/leave` | same | `messaging/contacts-and-groups` |
| Group invitation message (received) | `GET .../groups/join-info?code=` and `POST .../groups/join`; invite codes `GET .../groups/{id}/invite-code`. | same | `messaging/contacts-and-groups` |

### 1.5 Calls

| Green API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Calling API: `callsDial`, `callsAccept`, `callsReject`, `callsHangUp`, `callsGetIceServers`, `callsState`, a `callsRtc` WebSocket and a browser client library; one-to-one calls up to 90 minutes | Browser calls with client tokens and the call components; server calls with `@polymorfa/sdk` (`messaging.voip`, and `@polymorfa/sdk/calls` to speak and listen); `POST /messaging/voip/calls` places a call and `DELETE /messaging/voip/calls/{id}` ends it; reject with `POST /messaging/{connection}/calls/{callId}/reject`. | more | `calls/web`, `calls/server` |
| SIP | SIP trunks in both directions: `GET /platform/sip/endpoint`, `POST /platform/sip-trunks`. | more | `calls/sip-trunks` |
| Call recordings | Polymorfa does not record calls. | gap | `calls` |

### 1.6 MCP, SDKs and integrations

| Green API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Hosted MCP server at `mcp.green-api.com`, OAuth with the instance id and token | `https://api.polymorfa.com/mcp`, Streamable HTTP, Bearer credential (team key, project token with the `mcp` scope, or client token with the `mcp` action). 200+ tools. It cannot return QR or pairing codes; use QuickLink. | more | `development/mcp` |
| Libraries in Python, Go, Java, PHP, Node.js, HTML5, 1C, C++ and gRPC | OpenAPI 3.1 specs for the Messaging, Platform and Graph APIs, and `@polymorfa/sdk` for TypeScript (prerelease under the `dev` tag). Generate a client from the specs for other languages. | different | `get-started/development-environment` |
| Integrations (Make, n8n, Zapier and others) | Call the REST API from the platform's HTTP step, or connect through MCP. | different | `integrations/overview` |
| Meta-format webhooks and Graph API | `format:"meta"` webhooks and `/graph/whatsapp/{version}/...` | more | `api/graph/index` |

## 2. Auth and identifiers

### 2.1 Credentials

| Green API | Polymorfa | Notes |
| --- | --- | --- |
| `idInstance` (URL path) | Connection id (URL path, opaque decimal string). | Not a secret. Returned as `data.connection` when a QuickLink is created, and listed by `GET /platform/connections`. |
| `apiTokenInstance` (URL path secret) | No per-connection secret. Access comes from a credential. | One token per instance becomes one credential per scope of access. |
| `webhookUrlToken` | Webhook signing secret and optional custom headers. | See section 3. |
| `partnerToken` | Team key plus the Customers API. | |
| Browser use of instance credentials | Client token `pmfa_ct_...`, minted by your server with `POST /platform/client-tokens`, bound to one Connection and an action list. | The issuing credential needs the scopes it grants. |

Credentials: team key `pmfa_...` (all projects), project token `pmfa_pt_...` (one project, the least-privilege replacement for a per-instance token), client token `pmfa_ct_...`. A migration agent cannot mint keys. Ask the human to create a project token with `messages:write`, `contacts:read`, `webhooks:manage`, `connections:manage` and the group, contact and chat scopes each reference page lists, then set `POLYMORFA_KEY`.

### 2.2 Phone numbers and chat ids

- Green API `chatId`: digits plus a suffix, `79876543210@c.us`. Polymorfa `conversation.phoneNumber`: E.164 with `+`, `+79876543210`. The Graph API `to` takes digits without `+`.
- The returned `phoneNumber` is WhatsApp's resolved number and can differ from the input. Match conversations by `conversation.id` per Connection.
- Groups (`...@g.us`) and `@lid` ids do not convert. Polymorfa group ids are opaque decimals. Build a map once with `GET /messaging/{connection}/groups` and store `group.id`. Polymorfa user ids replace `@lid`; `phoneNumber`, `bsuid` and `username` are optional aliases and can be missing when WhatsApp hides the number. Reply to hidden-number senders with `conversation.id`.
- Green API `idMessage` becomes Polymorfa `id`. WhatsApp's id is in `whatsapp_ids.linked_devices`. Do not pass the WhatsApp id where `id` is expected. Keep both when migrating stored threads.
- Green API `timestamp` is Unix seconds. Polymorfa `payload.timestamp` is Unix seconds, and the envelope `timestamp` is ISO 8601.

## 3. Webhook migration

### 3.1 Transport

| Topic | Green API | Polymorfa |
| --- | --- | --- |
| Registration | `webhookUrl` and per-type flags in `SetSettings` | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` or `meta`), `retryPolicy`, `enabled`, custom headers. Needs `webhooks:manage`. Each mutation needs an `Idempotency-Key`. |
| Authentication | `webhookUrlToken` sent in the `Authorization` header (`Basic` or `Bearer`); IP allowlisting suggested. No payload signature documented. | HMAC-SHA256 over the exact raw body. `native`: `X-Webhook-Signature: <lowercase hex>`. `meta`: `X-Hub-Signature-256: sha256=<hex>`. Constant-time compare. Secret returned once on create; rotate with `POST .../secret-rotations`. |
| Retries | One attempt a minute for up to 24 hours | Up to 8 attempts over 24 hours at 30 s, 2 min, 10 min, 1 h, 4 h, 12 h and 24 h. Retries on network error, timeout, `408`, `429`, `5xx`. |
| Timeout | Not stated | 30 s per attempt, up to 3 redirects. Respond fast, process later. |
| Pull mode | `ReceiveNotification` and `DeleteNotification`, 24-hour queue | Not offered as a call. Use webhooks or an event stream (`GET /platform/projects/{projectId}/events/stream`, beta). |
| Trace and dedupe | none documented | `X-Polymorfa-Delivery-ID`, `X-Polymorfa-Delivery-Attempt`. The event `id` is stable across retries. Delivery is at least once and unordered. |
| Redelivery | none | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |

### 3.2 Envelope

```json
{
  "id": "<event id>",
  "connection": "739182640518203",
  "timestamp": "2026-10-19T10:05:00.000Z",
  "event": "message.received",
  "payload": { }
}
```

Green API `typeWebhook` becomes `event`. `instanceData.idInstance` becomes `connection`. The flat fields move under `payload`.

### 3.3 Events

| Green API `typeWebhook` | Polymorfa event | Notes |
| --- | --- | --- |
| `incomingMessageReceived` | `message.received`, plus `message.reaction`, `message.vote`, `message.edited`, `message.revoked` | `senderData.chatId` becomes `payload.conversation.id`; group senders are in `payload.conversation.sender`. `messageData.typeMessage` becomes `payload.type`. |
| `outgoingMessageStatus` (`sent`, `delivered`, `read`, `failed`, `noAccount`, `notInGroup`) | `message.sent`, `message.ack` (`type`: `delivered`, `read`, `played`, `error`), `message.failed` | `noAccount` and `failed` arrive as `message.failed`; read its `error` and `code`. |
| `outgoingAPIMessageReceived` | `message.sent` | |
| `outgoingMessageReceived` (sent from the phone) | `message.echo` on coexistence Connections | Not found for linked-device phone sends. |
| `stateInstanceChanged` | `connection.status` (`DISCONNECTED` with `statusReason`), `connection.connected`, `connection.logged_out`, `connection.restriction_updated` | `blocked` maps to `connection.logged_out` with `reason: banned`; `suspended` is closest to `connection.restriction_updated`. |
| `incomingCall` | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended` | |
| Edited and deleted message flags | `message.edited`, `message.revoked`, `message.delete` | |
| Selected buttons and list responses | `message.received` with `button_reply`, `list_reply` or `native_flow_response` | Key on `replyChoice.id`. |

`type` values on `message.received`: `text`, `image`, `video`, `audio`, `document`, `location`, `contact`, `phone_number_shared`, `native_flow_response`, `button_reply`, `list_reply`, `poll`, `sticker`, `sticker_pack`, `reaction`, `revoke`, `edited`, `unknown`. Media events carry a `media` reference, not a public URL.

### 3.4 What a migrating handler must change

1. Verify `X-Webhook-Signature` on the raw bytes first. This replaces the `webhookUrlToken` check.
2. Read `event`, not `typeWebhook`, and read the body under `payload`.
3. Key people by `conversation.id`; stop parsing `@c.us`, `@g.us` and `@lid`.
4. Replace `idMessage` with `payload.id` for actions; store `whatsapp_ids`.
5. Respond 2xx within 30 s after a durable save, dedupe on the envelope `id`, and accept reordering.
6. Subscribe to specific `eventTypes`.
7. Handle new events: `message.failed`, `connection.restriction_updated`, `bansafe.*`.

## 4. Gaps and behaviour differences a migrating agent must handle

Gaps (not offered):

1. Statuses (send, delete, statistics, history).
2. Address book contact methods (`addContact`, `editContact`, `deleteContact`).
3. Send-side link previews.
4. A readable send queue, and queued sends while a Connection is disconnected.
5. Pull-mode notifications (`ReceiveNotification`).
6. Call recordings.

Behaviour differences:

- **Queue on disconnect.** Green API keeps a queued message for up to 24 hours and sends it in order, spaced by `delaySendMessagesMilliseconds`. Polymorfa refuses a send to a disconnected Connection: `503 connection_not_ready` (synchronous) or `message.failed` with `connection_not_connected` (asynchronous, with `Prefer: respond-async`). The migrating app needs its own outbox. Use `Idempotency-Key` (1-hour window) so a retry cannot send twice. Do not retry on `bansafe_send_outcome_unknown`; read the message state first.
- **First messages to people who never wrote.** Outside Campaigns, a first message to such a contact is refused (`bansafe_cold_blocked`, `403`), and adding that person to a group is refused too. Route outreach through Campaigns (Pro) or message people who wrote first.
- **Pacing is enforced.** Warm-up allowance (`bansafe_daily_allowance_reached`, `429`), throttle (`bansafe_throttled`, `429`, `Retry-After`) and the WhatsApp new-chat cap (`new_chat_limit_reached`, `429`). Respect `Retry-After`.
- **Delays.** `delaySendMessagesMilliseconds` (500 to 600000 ms) and `autoTyping` (0 to 10) map to project Safe Mode (`pacing`, `typing`, `presence`, `reads`), all off by default, Standard or Pro only, owner or admin to change. Contacts see presence, typing and read receipts, which cannot be undone.
- **Media.** Green API returns file links through webhooks and `downloadFile`, and says storage is limited by WhatsApp. Polymorfa keeps no attachment files. Download on webhook receipt with `GET /messaging/media/{id}`, or save to your own bucket with `POST /messaging/media/{id}/download-and-save`.
- **IDs.** Everything is an opaque decimal string. Do not parse or cast it, and do not look for `@c.us`, `@g.us` or `@lid`. Remap stored group ids by listing groups.
- **Hosted history.** There is no equivalent of reading everything the phone holds. History needs hosted message storage (beta) and is bounded by retention.
- **Official API.** Green API sells the Business API as a separate WABA product. On Polymorfa a Cloud API Connection uses the same API as a linked-device Connection; the Connection you address decides the route. Cloud API onboarding is in beta.
- **Rate limits.** Green API limits requests per second per instance, with `429` above the limit. Polymorfa applies a team request quota (`429`, `Retry-After`, `X-RateLimit-*`) plus WhatsApp-side limits.
