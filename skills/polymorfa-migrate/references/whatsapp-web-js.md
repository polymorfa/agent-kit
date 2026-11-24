# whatsapp-web.js reference for polymorfa-migrate

Maps whatsapp-web.js (https://github.com/wwebjs/whatsapp-web.js, reference at https://docs.wwebjs.dev, version 1.34.8) to Polymorfa. Checked on 24 November 2026 against the library's README, guide and API reference, and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/whatsapp-web-js.

whatsapp-web.js is a free Node.js library (Apache-2.0) that runs WhatsApp Web in a Puppeteer browser inside the user's own process. It has no HTTP API, webhooks or credentials of its own: the user's code calls `client.*` methods and listens to `client.on(...)` events, and often wraps the client in its own Express or queue code. Search the repository for `whatsapp-web.js`, `new Client(`, `LocalAuth`, `RemoteAuth`, `client.on(`, `MessageMedia`, `puppeteer` and `.wwebjs_auth`. Also ask whether the user wrapped the client in an HTTP service, because that wrapper is what the Polymorfa API replaces.

## 1. Mapping

### 1.1 Sessions and lifecycle

| whatsapp-web.js | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `LocalAuth`, `RemoteAuth` (Mongo, S3 or custom store), `NoAuth`, `clientId`, `.wwebjs_auth` | Polymorfa stores each Connection's session. One Connection per number. Sessions cannot be imported (import covers Baileys and whatsmeow only); pair each number again | different | `connections/import-connections`, `connections/quicklink` |
| `qr` event, QR printed in a terminal | QuickLink hosted page, or `GET /messaging/{connection}/pair/qr` with direct pairing (needs access) | same | `connections/quicklink`, `connections/direct-pairing` |
| `client.requestPairingCode(phoneNumber)` | QuickLink pairing code, or `POST /messaging/{connection}/pair/code` with `{"phone":"+15550001111"}` | same | `connections/direct-pairing` |
| `client.getState()`, `ready`, `authenticated`, `change_state`, `disconnected`, `auth_failure` | `GET /platform/connections/{connectionId}` (`status`: `CONNECTING`, `CONNECTED`, `DISCONNECTED`); events `connection.connected`, `connection.status`, `connection.logged_out` | more | `connections/manage`, `api-events` |
| `client.destroy()` | `POST /platform/connections/{connectionId}/stop`; returns `202` with an operation id | same | `connections/manage` |
| `client.logout()` | `POST /platform/connections/{connectionId}/logout` unlinks the phone | same | `connections/manage` |
| Restarting the Node.js process | `POST /platform/connections/{connectionId}/restart` | same | `connections/manage` |
| Many `Client` objects for many customers | Customers API: customer records, pairing links and a monthly cap per customer | more | `customers` |
| `puppeteer` options, `--no-sandbox`, Chrome install, `webVersionCache`, `userAgent`, `proxyAuthentication` | No equivalent and none needed: there is no browser. Remove after traffic has moved. No proxy option | gap | none |

Pairing is done by a person. An agent cannot fetch or scan the QR code for the user.

## 2. Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?}`. Add an `Idempotency-Key` header. Address a person with `conversation.phoneNumber` in E.164 with a plus sign, not `15550001111@c.us`.

| whatsapp-web.js | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `client.sendMessage(chatId, 'text')`, `chat.sendMessage` | `content.text` | same | `messaging/send` |
| `MessageMedia` image, video, audio, document; `sendAudioAsVoice`, `sendMediaAsDocument`, `sendMediaAsHd` | `content.image`, `content.video`, `content.voice`, `content.file` with `url` or `base64`; `quality: hd` on images | same | `messaging/send`, `messaging/media` |
| `sendMediaAsSticker` | `content.sticker` | same | `messaging/stickers` |
| `Location`, contact cards (`parseVCards`) | `content.location`, `content.contact` (vCard) | same | `messaging/send` |
| `Poll` | `content.poll` (2 to 12 options, optional multiple select) | same | `messaging/send` |
| `Buttons`, `List` (marked deprecated in the README) | `content.buttons`, `content.list`; carousels in `content.carousel`; Cloud API templates and WhatsApp Flows | more | `messaging/send`, `messaging/templates`, `messaging/flows` |
| `message.reply()`, `quotedMessageId` | `quotedMessage.id` (Polymorfa message id) | same | `messaging/send` |
| `mentions` option, `@number` in text | `mentions` array of Polymorfa user ids (not phone numbers) | different | `messaging/send`, `messaging/ids` |
| `message.react()`, `client.sendReaction()` | `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| `message.edit()` | `PUT /messaging/{connection}/chats/{conversation}/messages/{messageId}`; linked devices only | same | `messaging/send` |
| `message.delete(true)` | `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `message.star()` | `POST /messaging/{connection}/messages/star` | same | `messaging/send` |
| `chat.sendSeen()`, `client.sendSeen()` | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| `chat.sendStateTyping()`, `chat.sendStateRecording()`, `sendPresenceAvailable()` | `POST /messaging/{connection}/messages/typing` with `state` of `typing`, `recording` or `paused`; presence events and subscriptions | more | `messaging/send`, `messaging/linked-device-controls` |
| `message.forward(chat)` | No forward-a-stored-message call. Send the content again with `isForwarded: true` | different | `messaging/send` |
| `sendVideoAsGif` | No GIF kind. Send an MP4 as `content.video` | gap | none |
| `isViewOnce` | Not offered | gap | none |
| `message.pin(duration)`, `chat.pin()`, `client.pinChat()` | Not offered | gap | none |
| Scheduled events (`sendResponseToScheduledEvent`, `editScheduledEvent`) | Not offered | gap | none |
| `message.vote(options)` | Not offered. Incoming votes arrive as `message.vote` | gap | `api-events` |
| Hand-written delays and typing before a send | Safe Mode `pacing` and `typing` on Standard and Pro Connections; warm-up and daily allowance are enforced | different | `safety/safe-mode` |

## 3. Groups, channels, contacts and labels

Ids differ: whatsapp-web.js uses `@c.us`, `@g.us`, `@lid` and `@newsletter` strings. Polymorfa group, user and message ids are opaque decimal strings. None carry over; list groups and contacts again after pairing.

| whatsapp-web.js | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `client.createGroup(title, participants)` | `POST /messaging/{connection}/groups` with user ids (resolve numbers with `contacts/check` first) | same | `messaging/contacts-and-groups` |
| `addParticipants`, `removeParticipants`, `promoteParticipants`, `demoteParticipants` | `POST .../groups/{id}/participants/add`, `.../participants/remove`, `.../admin/promote`, `.../admin/demote` | same | `messaging/contacts-and-groups` |
| `setSubject`, `setDescription`, `setPicture`, `deletePicture` | `PUT .../groups/{id}/subject`, `.../description`, `.../picture` | same | `messaging/contacts-and-groups` |
| `setMessagesAdminsOnly`, `setInfoAdminsOnly`, `setAddMembersAdminsOnly` | Group settings: `settings/messages`, `settings/info-edit`, `settings/member-add`, `settings/join-approval` | same | `messaging/linked-device-controls` |
| `getInviteCode`, `revokeInvite`, `client.acceptInvite`, `getInviteInfo` | `GET .../groups/{id}/invite-code`, `POST .../invite-code/revoke`, `POST .../groups/join`, `GET .../groups/join-info` | same | `messaging/contacts-and-groups` |
| `leave()` | `POST .../groups/{id}/leave` | same | `messaging/contacts-and-groups` |
| `getGroupMembershipRequests`, `approveGroupMembershipRequests`, `rejectGroupMembershipRequests` | Not offered on linked-device Connections | gap | none |
| `client.createChannel`, `deleteChannel`, `subscribeToChannel`, `unsubscribeFromChannel`, mute | `POST /messaging/{connection}/channels`, `DELETE .../channels/{id}`, `.../follow`, `.../unfollow`, `.../mute`, `.../unmute`; read with `GET .../channels/{id}/messages` | same | `messaging/channels` |
| `searchChannels`, `getSubscribers`, channel admin invites, ownership transfer, subject, description, picture | Not offered | gap | none |
| `getNumberId`, `isRegisteredUser` | `GET /messaging/{connection}/contacts/check` (up to 1,000 numbers) | same | `messaging/user-identities` |
| `getContacts`, `getContactById`, `getProfilePicUrl`, `getAbout` | `GET .../contacts`, `GET .../contacts/{contactId}`, `.../picture`, `.../info` | same | `messaging/user-identities` |
| `contact.block()`, `contact.unblock()`, `getBlockedContacts` | `POST .../contacts/{contactId}/block`, `.../unblock`, `GET .../contacts/blocked` | same | `messaging/user-identities` |
| `setStatus`, `setDisplayName`, `setProfilePicture` | `PUT .../profile/status`, `.../profile/name`, `.../profile/picture` | same | `messaging/contacts-and-groups` |
| `getLabels`, `getChatLabels`, `chat.changeLabels`, `addOrRemoveLabels` | `GET` and `POST .../labels`, `PUT` and `DELETE .../labels/{labelId}`, `PUT .../labels/chats/{conversation}` (replaces the whole set) | same | `messaging/linked-device-controls` |
| `chat.archive()`, `chat.unarchive()` | `POST .../chats/{conversation}/archive` and `.../unarchive` | same | `messaging/send` |
| `chat.mute()`, `chat.clearMessages()`, `chat.delete()`, `markUnread`, customer notes | Not offered as calls. Chat events exist | gap | `api-events` |
| Communities | Not offered (not in whatsapp-web.js either; its README lists them as coming) | gap | none |

## 4. Events and webhooks

whatsapp-web.js emits events in-process. Replace them with one Polymorfa webhook: create it with `POST /platform/projects/{projectId}/webhooks`, pick `eventTypes`, store the signing secret, and verify `X-Webhook-Signature` (HMAC-SHA256 over the raw body) before processing. Deliveries retry up to 8 times over 24 hours; there is a delivery log and replay.

| whatsapp-web.js event | Polymorfa event | Status | Docs page |
| --- | --- | --- | --- |
| `message` | `message.received` | same | `messaging/receive` |
| `message_create` (own messages) | `message.sent`, `message.failed` for sends through the API | different | `api-events` |
| `message_ack` | `message.ack` (`delivered`, `read`, `played`, `error`) | same | `api-events` |
| `message_reaction` | `message.reaction` | same | `messaging/receive` |
| `message_edit` | `message.edited` | same | `messaging/receive` |
| `message_revoke_everyone`, `message_revoke_me` | `message.revoked`, `message.delete` | same | `messaging/receive` |
| `vote_update` | `message.vote` | same | `messaging/receive` |
| `group_join`, `group_leave`, `group_admin_changed` | `group.participant` | same | `api-events` |
| `group_update` | `group.update` | same | `api-events` |
| `group_membership_request` | Not offered | gap | none |
| `contact_changed` | `contact.update` | same | `api-events` |
| `chat_archived`, `chat_removed` | Chat events such as `chat.archive` and `chat.delete` | same | `api-events` |
| `call` | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended` and more | more | `calls/how-calls-work` |
| `change_battery`, `media_uploaded`, `message_ciphertext` | Not offered | gap | none |

## 5. Calls

| whatsapp-web.js | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `Call` object with `from`, `isVideo`, `isGroup`, `id` and one method, `reject()` | `call.received` webhook, then `POST /messaging/voip/calls/{id}/reject`, or accept | more | `calls/server` |
| Placing or answering a call (not supported) | `POST /messaging/voip/calls` places a call; accept answers. Browser calls with client tokens; server audio with `CallsClient` from the SDK; SIP trunks for a PBX | more | `calls/server`, `calls/web`, `calls/sip-trunks` |
| `createCallLink` | Not offered | gap | none |

## 6. History and media

| whatsapp-web.js | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `getChats`, `chat.fetchMessages`, `syncHistory`, `searchMessages` | Message history API (beta): `GET /messaging/{connection}/chats`, `.../chats/{conversation}/messages`. Needs hosted message storage and joining the history beta; contains only messages after storage was on. Otherwise store events as they arrive | different | `messaging/history` |
| `message.downloadMedia()`, `downloadMediaStream` | Events carry a `media` reference. Download with `GET /messaging/media/{id}`, or save to the user's own storage with `POST /messaging/media/{id}/download-and-save`. Polymorfa keeps no hosted copy of received media | different | `messaging/media` |

## 7. Behavior to carry over

- A send to a disconnected Connection fails at once with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it.
- Both whatsapp-web.js and Polymorfa linked-device Connections are linked devices on the phone. Keep the old client linked only while testing, do not send from both for one conversation, and stop it after the number's traffic has moved.
- The user's own HTTP wrapper around the client (routes, queues, auth) is replaced by the Polymorfa API and webhooks; do not port it.

## 8. AI agents

whatsapp-web.js has no MCP server. Polymorfa has a hosted MCP server with 200+ tools (`development/mcp`). It cannot return QR codes or pairing codes; use QuickLink.
