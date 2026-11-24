# Evolution API reference for polymorfa-migrate

Maps Evolution API (https://docs.evolutionfoundation.com.br, repository https://github.com/evolution-foundation/evolution-api) to Polymorfa. Checked on 24 November 2026 against Evolution API 2.3.8, its published OpenAPI definitions and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/evolution-api.

Evolution API is self-hosted software the user runs. Polymorfa is operated. Ask which instances use the Baileys integration (`WHATSAPP-BAILEYS`) and which use the Cloud API integration (`WHATSAPP-BUSINESS`) before you map anything.

## Requests and credentials

| Evolution API | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `{EVOLUTION_URL}/{group}/{method}/{instanceName}` with an `apikey` header (global key or instance key) | `https://api.polymorfa.com/messaging/{connection}/...` with `Authorization: Bearer <API key>`; short-lived client tokens for browsers | more | `development/api-keys`, `development/client-tokens` |
| `number` as digits or a JID | `conversation.phoneNumber` in E.164 with a plus sign, such as `+5511999990000` | different | `messaging/send` |
| Message `key` (`id`, `remoteJid`) in the response | `id` (Polymorfa message id) and `whatsapp_ids` | different | `messaging/ids` |

## Instances and pairing

| Evolution API | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `POST /instance/create`, `GET /instance/connect/{instance}` | QuickLink, or `GET /messaging/{connection}/pair/qr` and `POST /messaging/{connection}/pair/code` with direct pairing | same | `connections/quicklink`, `connections/direct-pairing` |
| `GET /instance/connectionState/{instance}` | `GET /platform/connections/{connectionId}`; event `connection.status` | same | `connections/manage` |
| `GET /instance/fetchInstances` | `GET /platform/connections` | same | `connections/manage` |
| `POST /instance/restart/{instance}` | `POST /platform/connections/{connectionId}/restart`; returns `202` with an operation id, then wait for `connection.status` | same | `connections/manage` |
| `DELETE /instance/logout/{instance}` | `POST /platform/connections/{connectionId}/logout` | same | `connections/manage` |
| `DELETE /instance/delete/{instance}` | `DELETE /platform/connections/{connectionId}` | same | `connections/manage` |
| One instance and token per client | Customers: customer records, pairing links and a monthly cap | more | `customers`, `customers/pairing-links` |
| `integration: WHATSAPP-BUSINESS` with a permanent token and number id | Cloud API Connection through Embedded Signup, in beta and needing access | different | `connections/cloud-api-setup` |
| Settings `rejectCall`, `msgCall` | `PUT /platform/connections/{connection}/call-settings` | different | `calls/server` |
| Settings `readMessages`, `alwaysOnline` | Project Safe Mode reads and presence | different | `safety/safe-mode` |
| Settings `groupsIgnore`, `readStatus` | No equivalent. Filter events in the application. | gap | none |
| `POST /proxy/set/{instance}` | No per-Connection proxy. | gap | none |
| Baileys session state in the user's database, Redis or files | Import a Baileys `SignalStoreSnapshot` (preview) into a Connection reserved through QuickLink with `POST /platform/connections/{id}/handoff-keys` and `handoff-import`. Evolution API has no export route: the snapshot is built from the stored state. Stop the Evolution instance first and keep it offline until the Connection reports `CONNECTED`. If the snapshot cannot be built, pair again with QuickLink. | different | `connections/import-connections` |

## Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?}`. Add an `Idempotency-Key` header.

| Evolution API | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `/message/sendText` | `content.text` | same | `messaging/send` |
| `/message/sendMedia` (image, video, document, audio) | `content.image`, `content.video`, `content.file`, `content.voice` with `url` or `base64` | same | `messaging/send`, `messaging/media` |
| `/message/sendWhatsAppAudio` | `content.voice` with `ptt: true` | same | `messaging/send` |
| `/message/sendSticker` | `content.sticker` | same | `messaging/stickers` |
| `/message/sendLocation`, `/message/sendContact` | `content.location`, `content.contact` | same | `messaging/send` |
| `/message/sendButtons` (reply, copy, url, call, pix) | `content.buttons` with `reply`, `url`, `call`, `copy` controls. No PIX button: use a `copy` control carrying the key. | more | `messaging/send` |
| `/message/sendList` | `content.list` | same | `messaging/send` |
| `/message/sendPoll` | `content.poll` | same | `messaging/send` |
| `/message/sendTemplate`, `/template/create`, `edit`, `delete`, `find` | `content.template`; template create, edit, preview and submit to Meta | same | `messaging/templates` |
| `/message/sendReaction` | `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| `quoted` | `quotedMessage.id` | same | `messaging/send` |
| `mentioned` | `mentions` (Polymorfa user ids, not numbers). No mention-all shortcut. | different | `messaging/send` |
| `delay`, `presence` options per send | No per-send field. Safe Mode pacing and typing, or `POST /messaging/{connection}/messages/typing` before a send. | different | `safety/safe-mode` |
| `linkPreview`, `mentionsEveryOne`, `encoding`, `webhookUrl` options | No equivalent. | gap | none |
| `/message/sendStatus` | Not offered. | gap | none |
| `/message/sendPtv` | Not offered. | gap | none |
| `/chat/markMessageAsRead` | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| `/chat/updateMessage` | `PUT /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `/chat/deleteMessageForEveryone` | `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `/chat/sendPresence`, `/instance/setPresence` | `POST /messaging/{connection}/messages/typing`, `POST /messaging/{connection}/presence` | same | `messaging/linked-device-controls` |
| Bulk sending loops | Campaigns with audiences, opt-outs and per-recipient status; Pro connections | more | `campaigns/send` |

## Groups, contacts and chats

Group ids are opaque, not `@g.us`.

| Evolution API | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `/group/create`, `findGroupInfos`, `fetchAllGroups`, `participants` | `POST /messaging/{connection}/groups`, `GET .../groups/{id}`, `GET .../groups`, `GET .../groups/{id}/participants` | same | `messaging/contacts-and-groups` |
| `/group/updateGroupSubject`, `updateGroupDescription`, `updateGroupPicture` | `PUT .../groups/{id}/subject`, `/description`, `/picture` | same | `messaging/contacts-and-groups` |
| `/group/updateParticipant` (`add`, `remove`, `promote`, `demote`) | `POST .../groups/{id}/participants/add`, `/participants/remove`, `/admin/promote`, `/admin/demote` | same | `messaging/contacts-and-groups` |
| `/group/inviteCode`, `revokeInviteCode`, `inviteInfo`, `acceptInviteCode` | `GET .../groups/{id}/invite-code`, `POST .../invite-code/revoke`, `GET .../groups/join-info`, `POST .../groups/join` | same | `messaging/contacts-and-groups` |
| `/group/updateSetting`, `leaveGroup` | The four `PUT .../groups/{id}/settings/*` calls, `POST .../groups/{id}/leave` | same | `messaging/linked-device-controls` |
| `/group/toggleEphemeral` | `PUT /messaging/{connection}/chats/{conversation}/disappearing` | same | `messaging/linked-device-controls` |
| `/chat/whatsappNumbers` | `GET /messaging/{connection}/contacts/check` | same | `messaging/contacts-and-groups` |
| `/chat/findContacts`, `/chat/fetchProfilePictureUrl`, `/chat/fetchProfile` | `GET /messaging/{connection}/contacts`, `.../contacts/{contactId}/picture`, `.../contacts/{contactId}/info` | same | `messaging/contacts-and-groups` |
| `/chat/updateBlockStatus` | `POST .../contacts/{contactId}/block` and `/unblock` | same | `messaging/linked-device-controls` |
| `/chat/archiveChat` | `POST .../chats/{conversation}/archive` and `/unarchive` | same | `messaging/linked-device-controls` |
| `/chat/markChatUnread` | Not offered. | gap | none |
| `/label/findLabels`, `/label/handleLabel` | `GET /messaging/{connection}/labels`, `PUT .../labels/chats/{conversation}` | same | `messaging/linked-device-controls` |
| `/chat/updateProfileName`, `updateProfileStatus`, `updateProfilePicture`, `removeProfilePicture` | `PUT .../profile/name`, `/profile/status`, `/profile/picture`, `DELETE .../profile/picture` | same | `messaging/linked-device-controls` |
| `/chat/fetchPrivacySettings`, `updatePrivacySettings` | `GET .../privacy`, `PUT .../privacy/{setting}` | same | `messaging/linked-device-controls` |
| `/chat/findChats`, `findMessages`, `findStatusMessage` from the user's own database | `GET .../chats`, `GET .../chats/{conversation}/messages`; beta, needs hosted message storage and joining the history beta. Otherwise store events as they arrive. | different | `messaging/history` |
| `/chat/getBase64FromMediaMessage` | `GET .../chats/{conversation}/messages/{messageId}/media` (hosted message storage), or download from the message event | different | `messaging/media` |
| `/business/getCatalog`, `getCollections` | `GET .../business/catalog`, `GET .../business/collections` on Business App Connections | same | `connections/catalog` |

## Webhooks and events

Evolution API sets a webhook per instance (`POST /webhook/set/{instance}`) or one global webhook, optionally with the event name added to the URL. Its only authentication is an optional bearer JWT, not a payload signature. It retries a failed delivery 10 times by default and does not retry 400, 401, 403, 404 or 422. Polymorfa: one signed endpoint (`X-Webhook-Signature`, HMAC-SHA256 of the raw body), up to 8 attempts over 24 hours, delivery log and replay. Event streams (beta) and Drains cover WebSocket and broker delivery.

| Evolution API event | Polymorfa event | Status | Docs page |
| --- | --- | --- | --- |
| `MESSAGES_UPSERT` | `message.received`, `message.reaction`, `message.vote`, `message.edited` | more | `development/webhooks`, `api-events` |
| `SEND_MESSAGE` | `message.sent`, `message.failed` | same | `api-events` |
| `MESSAGES_UPDATE` | `message.ack`, `message.update` | same | `api-events` |
| `MESSAGES_DELETE` | `message.revoked`, `message.delete` | same | `api-events` |
| `CONNECTION_UPDATE` | `connection.status`, `connection.connected`, `connection.logged_out` | more | `api-events` |
| `QRCODE_UPDATED` | Not needed with QuickLink | different | `connections/quicklink` |
| `PRESENCE_UPDATE` | `presence.update` | same | `api-events` |
| `CHATS_UPDATE`, `CHATS_DELETE` | `chat.archive`, `chat.read`, `chat.mute`, `chat.clear`, `chat.delete` | same | `api-events` |
| `GROUPS_UPSERT`, `GROUPS_UPDATE`, `GROUP_PARTICIPANTS_UPDATE` | `group.update`, `group.participant` | same | `api-events` |
| `CONTACTS_SET`, `CONTACTS_UPSERT`, `CONTACTS_UPDATE`, `CHATS_SET`, `CHATS_UPSERT`, `MESSAGES_SET`, `APPLICATION_STARTUP`, `NEW_TOKEN` | No direct equivalent. Read contacts and chats through the API. | gap | none |

## Calls

Evolution API has `POST /call/offer/{instance}`, but its linked-device channel returns a fixed placeholder instead of placing a call, and the `wavoipToken` setting connects a third-party service. Polymorfa places and answers calls in a browser, from server code and over SIP trunks, with `call.*` events (`calls`, `calls/server`, `calls/sip-trunks`). Polymorfa does not record calls.

## Integrations with no equivalent

Chatwoot, Typebot, OpenAI, Dify, Flowise, EvoAI and Evolution Bot integrations, and the S3 and MinIO storage option. Polymorfa does not offer them. The application keeps this logic, and the UI Kit (`ui-kit/inbox`) has inbox components to build screens. Polymorfa does not host media files: download media from its message or save it to the customer's own storage with `POST /messaging/media/{id}/download-and-save`.

## Behavior to carry over

- A send to a disconnected Connection fails at once with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it.
- Evolution API identifiers (instance names, JIDs, message keys) do not carry over. Polymorfa ids are opaque strings (`messaging/ids`).
- Never run an Evolution instance and the imported Polymorfa Connection at the same time.

## AI agents

Polymorfa has a hosted MCP server with 200+ tools (`development/mcp`).
