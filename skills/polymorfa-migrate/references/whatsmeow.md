# whatsmeow reference for polymorfa-migrate

Maps the whatsmeow Go library (https://github.com/tulir/whatsmeow, reference at https://pkg.go.dev/go.mau.fi/whatsmeow) to Polymorfa. Checked on 24 November 2026 against whatsmeow's README, Go reference, events package and device store schema, and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/whatsmeow.

whatsmeow is a library that runs inside the user's Go process. It has no HTTP API, no webhooks and no credentials. Polymorfa is an HTTP API. Polymorfa's linked-device connections run on HyperMeow, an engine built on whatsmeow, so the linked-device behavior is familiar. whatsmeow has no tagged releases; ask the user which commit their go.mod pins.

## Move the session first

Offer connection import before anything else. It moves a whatsmeow linked device to Polymorfa so the phone stays linked and nobody scans a QR code again. Docs page: `connections/import-connections`.

- Import is in preview. whatsmeow sessions move through an assisted migration; the Console does not accept raw database uploads. The user contacts Polymorfa (https://www.polymorfa.com/contact?subject=Migration).
- The user reserves a destination Connection through QuickLink (`connections/quicklink`) first.
- The source must stay offline. Two copies of one linked device compete and WhatsApp can invalidate the connection. The whatsmeow client stays stopped from the snapshot until Polymorfa reports the imported Connection as connected (`status` is `CONNECTED`, or the `connection.connected` event).
- Snapshot the store once and consistently: the device record (`whatsmeow_device`) and the Signal tables. Leave the original store unchanged until the imported Connection is connected.
- Do not run the import yourself and do not ask for the database contents. Ask the user to start it.
- If the user prefers, pair again through QuickLink.

## Requests and credentials

| whatsmeow | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `client.SendMessage(ctx, jid, *waE2E.Message)` | `POST /messaging/{connection}/messages/send` with `Authorization: Bearer <API key>` | different | `messaging/send`, `development/api-keys` |
| Access control in the user's own server | API keys with scopes; short-lived client tokens for browsers | more | `development/api-keys`, `development/client-tokens` |
| `types.JID` (`...@s.whatsapp.net`, `...@lid`, `...@g.us`) | Opaque string ids; `conversation.phoneNumber` with a plus sign for a first send. JIDs do not convert. | different | `messaging/ids` |

## Pairing and sessions

| whatsmeow | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `GetQRChannel` | QuickLink, or `GET /messaging/{connection}/pair/qr` with direct pairing access | same | `connections/quicklink`, `connections/direct-pairing` |
| `PairPhone` | QuickLink pairing code, or `POST /messaging/{connection}/pair/code` | same | `connections/direct-pairing` |
| `sqlstore` device container | Stored by Polymorfa with the session and its keys; moved by connection import | different | `connections/import-connections` |
| `Connect`, `Disconnect` | `POST /platform/connections/{connectionId}/restart` and `/stop`; each returns `202` with an operation id | same | `connections/manage` |
| `Logout` | `POST /platform/connections/{connectionId}/logout` | same | `connections/manage` |
| `IsConnected`, `IsLoggedIn` | `GET /platform/connections/{connectionId}`; `connection.status` event | more | `connections/manage` |
| `GetAllDevices`, one client per device | One Connection per phone; Customers group Connections with a monthly cap and pairing links | more | `customers` |
| `SetProxy`, `SetSOCKSProxy` | Not offered. | gap | none |

## Sending

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?}`. Add an `Idempotency-Key` header.

| whatsmeow | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `Conversation`, `ExtendedTextMessage` | `content.text` | same | `messaging/send` |
| `Upload` plus `ImageMessage`, `VideoMessage`, `AudioMessage`, `DocumentMessage`, `StickerMessage` | `content.image`, `video`, `voice`, `file`, `sticker` with `url` or `base64` | same | `messaging/send`, `messaging/media` |
| `LocationMessage`, `ContactMessage` | `content.location`, `content.contact` | same | `messaging/send` |
| `BuildPollCreation` | `content.poll` | same | `messaging/send` |
| `BuildEdit` | `PUT /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `BuildRevoke` | `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` | same | `messaging/send` |
| `BuildReaction` | `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| `MarkRead` | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| `SendChatPresence` | `POST /messaging/{connection}/messages/typing` | same | `messaging/send` |
| `SendPresence`, `SubscribePresence` | `POST /messaging/{connection}/presence/{conversation}/subscribe`; `presence.update` events | same | `messaging/linked-device-controls` |
| `SetDisappearingTimer` | `PUT /messaging/{connection}/chats/{conversation}/disappearing` | same | `messaging/linked-device-controls` |
| Quoted message in `ContextInfo` | `quotedMessage.id` | same | `messaging/send` |
| Status messages | Not offered. | gap | none |
| Broadcast list messages | Not offered. Campaigns send individual messages with opt-outs. | gap | `campaigns` |

## Groups, channels and contacts

| whatsmeow | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `CreateGroup`, `GetJoinedGroups`, `GetGroupInfo` | `POST` and `GET /messaging/{connection}/groups`, `GET .../groups/{id}`. Participants are user ids. | same | `messaging/contacts-and-groups` |
| `UpdateGroupParticipants` | `POST .../groups/{id}/participants/add` and `/remove`; `.../admin/promote` and `/demote` | same | `messaging/contacts-and-groups` |
| `SetGroupName`, `SetGroupTopic`, `SetGroupPhoto` | `PUT .../groups/{id}/subject`, `/description`, `/picture` | same | `messaging/contacts-and-groups` |
| `SetGroupAnnounce`, `SetGroupLocked`, `SetGroupMemberAddMode`, `SetGroupJoinApprovalMode` | Group settings operations under `.../groups/{id}/settings/` | same | `messaging/linked-device-controls` |
| `GetGroupInviteLink`, `JoinGroupWithLink`, `LeaveGroup` | `GET .../groups/{id}/invite-code`, `POST .../groups/join`, `POST .../groups/{id}/leave` | same | `messaging/contacts-and-groups` |
| `GetGroupRequestParticipants`, `UpdateGroupRequestParticipants` | Not offered. | gap | none |
| `LinkGroup`, `GetSubGroups` (communities) | Not offered. | gap | none |
| `CreateNewsletter`, `FollowNewsletter`, `GetNewsletterMessages` and related | Channel operations under `/messaging/{connection}/channels`: create, follow, mute, read, react | different | `messaging/channels` |
| `IsOnWhatsApp` | `GET /messaging/{connection}/contacts/check` | same | `messaging/user-identities` |
| `GetUserInfo`, `GetProfilePictureInfo`, `GetBusinessProfile` | Contact info, picture and business profile operations | same | `messaging/contacts-and-groups`, `messaging/linked-device-controls` |
| `GetBlocklist`, `UpdateBlocklist` | `GET .../contacts/blocked`, `POST .../contacts/{contactId}/block` and `/unblock` | same | `messaging/user-identities` |
| `GetPrivacySettings`, `SetPrivacySetting` | `GET /messaging/{connection}/privacy`, `PUT .../privacy/{setting}` | same | `messaging/linked-device-controls` |

## Media and history

| whatsmeow | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| `Download`, `DownloadToFile` | No hosted copy. Download from the message while WhatsApp serves it, or `POST /messaging/media/{id}/download-and-save` to the user's own storage | different | `messaging/media` |
| `events.HistorySync`, `DownloadHistorySync` | No equivalent push. Message history API (beta, needs the opt-in feature and hosted message storage on the Connection) | different | `messaging/history` |

## Events

Create one signed webhook for the events the user picks. Verify `X-Webhook-Signature` (HMAC-SHA256 of the raw body) on every delivery. Up to 8 attempts over 24 hours; delivery log and replay.

| whatsmeow event | Polymorfa event | Status | Docs page |
| --- | --- | --- | --- |
| `AddEventHandler` | One webhook endpoint with an `eventTypes` list | more | `development/webhooks` |
| `events.Message` | `message.received`, `message.reaction`, `message.vote`, `message.edited`, `message.revoked` | same | `api-events` |
| `events.Receipt` | `message.ack` | same | `api-events` |
| `events.Presence`, `events.ChatPresence` | `presence.update` (on once the project enables presence) | same | `messaging/linked-device-controls` |
| `events.Connected`, `events.Disconnected` | `connection.connected`, `connection.status` | same | `api-events` |
| `events.LoggedOut`, `events.TemporaryBan` | `connection.logged_out` with a reason, and BanSafe incident events | more | `api-events`, `safety/health` |
| `events.StreamReplaced` | Not needed: Polymorfa runs one session per Connection. | different | none |
| `events.GroupInfo`, `events.JoinedGroup` | `group.update`, `group.participant` | same | `api-events` |
| `events.CallOffer`, `events.CallAccept`, `events.CallTerminate` | `call.received`, `call.accepted`, `call.ended` and the other call events | more | `calls/how-calls-work` |
| `events.LabelEdit`, `events.LabelAssociationChat` | `labels.update` | same | `api-events` |

## Calls

whatsmeow reports call events and can reject a call (`RejectCall`); its README lists calls as not yet implemented. Polymorfa places and answers calls: `POST /messaging/voip/calls` from a server, the browser components, or a SIP trunk (`calls/server`, `calls/web`, `calls/sip-trunks`). Reject: `POST /messaging/{connection}/calls/{callId}/reject`.

## Behavior to carry over

- A send to a disconnected Connection fails at once with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it.
- Messages are JSON content kinds, not `waE2E` protobufs. Replace the builders instead of converting them.
- Pacing and typing come from Safe Mode project settings (`safety/safe-mode`). Respect `Retry-After` on `429`.

## AI agents

Polymorfa has a hosted MCP server with 200+ tools (`development/mcp`).
