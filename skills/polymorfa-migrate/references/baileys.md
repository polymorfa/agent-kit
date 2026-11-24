# Baileys reference for polymorfa-migrate

Maps Baileys (https://github.com/WhiskeySockets/Baileys, guide at https://baileys.wiki) to Polymorfa. Checked on 24 November 2026 against Baileys' published guide and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/baileys.

Baileys is an open-source (MIT) TypeScript library, `@whiskeysockets/baileys`. It runs a WhatsApp Web linked device inside the user's process: no hosted API, no webhooks, no database. Polymorfa runs the same kind of linked device as a service. Ask which Baileys version the project uses (6.x, 7.0.0-rc, or a fork) and whether the auth state is `useMultiFileAuthState` or a custom `SignalKeyStore`.

## Requests and credentials

Baileys: no network credential. `makeWASocket({ auth: state })` holds the session in the process, and `creds.update` must be saved or messages fail to send or decrypt.

Polymorfa: `Authorization: Bearer <project token or team key>` with scopes such as `messages:write` and `connections:manage`. Browsers use a short-lived client token bound to one Connection. Native paths start with `https://api.polymorfa.com/messaging/{connection}` or `https://api.polymorfa.com/platform`. The Connection id is not a secret.

## Moving the session (import)

Connection import moves a Baileys linked device to Polymorfa without pairing the phone again. It is in preview. Page: `connections/import-connections`.

1. Reserve a destination Connection through QuickLink (`POST /messaging/quicklinks`; the id is `data.connection`).
2. Stop the Baileys process and every write to its auth state. Take the `SignalStoreSnapshot`.
3. `POST /platform/connections/{connectionId}/handoff-keys` returns `runnerPublicKeyB64` (Curve25519, base64url, no padding) and `handoffId`.
4. Seal the snapshot JSON to that key as a sealed box (32-byte ephemeral public key followed by the ciphertext, base64). Compute the SHA-256 of the unsealed snapshot JSON as hex.
5. `POST /platform/connections/{connectionId}/handoff-import` with `handoffId`, `sealedEnvelopeB64` and `snapshotHashHex`. Polymorfa verifies the hash after decrypting.
6. Wait for status `CONNECTED` or the `connection.connected` event, send a test message, then move traffic.

Limits to agree with the user:

- Never run the Baileys process and the imported copy together. Two copies of one linked device compete and WhatsApp can invalidate the connection. Keep Baileys offline until the Connection is connected.
- A Baileys session moves as a `SignalStoreSnapshot`. If the user's store cannot produce one, pair again through QuickLink.
- Keep a backup of the Baileys auth state until the user is sure.
- Import needs the `connections:manage` scope.

## Mapping

| Baileys capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| QR code from `connection.update` | QuickLink, or `GET /messaging/{connection}/pair/qr` (direct pairing, needs team access) | same | `connections/quicklink`, `connections/direct-pairing` |
| `sock.requestPairingCode(number)` | QuickLink pairing code, or `POST /messaging/{connection}/pair/code` with `{"phone":"+15550001111"}` | same | `connections/direct-pairing` |
| `useMultiFileAuthState`, custom `SignalKeyStore`, `creds.update` | Stored by Polymorfa. Import an existing session; nothing to save | more | `connections/import-connections` |
| Reconnect on `restartRequired`, `loggedOut` (401) | `POST /platform/connections/{connectionId}/restart` (`202` with an operation id), `POST .../logout`, `GET /platform/connections/{connectionId}`; events `connection.status`, `connection.connected`, `connection.logged_out` | more | `connections/manage` |
| One socket per customer | Customers: customer records, pairing links and a monthly cap per customer | more | `customers` |
| `sendMessage` with `text` | `POST /messaging/{connection}/messages/send` with `content.text` | same | `messaging/send` |
| `image`, `video`, `audio`, `document`, sticker | `content.image`, `video`, `voice` (`ptt:true` for a voice note), `file`, `sticker`, by `url` or `base64` | same | `messaging/send`, `messaging/media` |
| `location`, `contacts` (vCard) | `content.location`, `content.contact:{vcard}` | same | `messaging/send` |
| `poll`, `react` | `content.poll` (2 to 12 options, `multiSelect`), `POST /messaging/{connection}/messages/react` | same | `messaging/send` |
| `quoted` | `quotedMessage:{id}` (Polymorfa message id) | same | `messaging/send` |
| `mentions` (JIDs) | `mentions:[<user id>]` (up to 256; user ids, not numbers) | different | `messaging/send` |
| `forward` | `isForwarded:true` on a new send. No "forward this stored message" call | different | `messaging/send` |
| `edit: key`, `delete: key` | `PUT` and `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` (linked device) | same | `messaging/send` |
| `readMessages` | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| `sendPresenceUpdate` (`composing`, `recording`, `paused`) | `POST /messaging/{connection}/messages/typing` with `state` `typing`, `recording` or `paused`; Safe Mode adds pacing and typing | more | `messaging/send`, `safety/safe-mode` |
| Send with `gifPlayback`, `ptv`, `viewOnce`, `pin` | Not offered. Send an MP4 as `content.video` | gap | none |
| Link preview from `link-preview-js` | No send-side preview field. Put the URL in `content.text` | different | `messaging/media` |
| Buttons and lists | `content.buttons`, `content.list`, `content.carousel` (Cloud API needs templates) | more | `messaging/send` |
| `groupCreate`, `groupLeave` | `POST /messaging/{connection}/groups` (`{name, participants:[user id]}`), `POST .../groups/{id}/leave` | same | `messaging/contacts-and-groups` |
| `groupParticipantsUpdate` | `POST .../groups/{id}/participants/add`, `.../participants/remove`, `.../admin/promote`, `.../admin/demote` | same | `messaging/contacts-and-groups` |
| `groupUpdateSubject`, `groupUpdateDescription` | `PUT .../groups/{id}/subject`, `PUT .../groups/{id}/description` | same | `messaging/contacts-and-groups` |
| `groupSettingUpdate`, `groupMemberAddMode` | `PUT .../groups/{id}/settings/info-edit`, `settings/messages`, `settings/member-add`, `settings/join-approval` | same | `messaging/linked-device-controls` |
| `groupInviteCode`, `groupRevokeInvite`, `groupAcceptInvite`, `groupGetInviteInfo` | `GET .../groups/{id}/invite-code`, `POST .../groups/{id}/invite-code/revoke`, `POST .../groups/join`, `GET .../groups/join-info?code=` | same | `messaging/contacts-and-groups` |
| `groupMetadata`, `groupFetchAllParticipating` | `GET .../groups/{id}`, `GET .../groups` | same | `messaging/contacts-and-groups` |
| `groupRequestParticipantsList`, `groupRequestParticipantsUpdate` (join requests) | Not offered | gap | none |
| Status updates (`status@broadcast`) | Not offered | gap | none |
| Broadcast lists | Campaigns: audiences, opt-outs, pacing and per-recipient status | more | `campaigns` |
| `messaging-history.set`, `fetchMessageHistory` | `GET /messaging/{connection}/chats` and `.../chats/{conversation}/messages` for Connections with hosted message storage, in beta (team opt-in); only messages after storage was enabled | different | `messaging/history` |
| `downloadMediaMessage`, `updateMediaMessage` | Download media from its message while WhatsApp serves it, or save it with `POST /messaging/media/{id}/download-and-save`. Polymorfa does not host media files | different | `messaging/media` |
| `call` event, `sock.rejectCall(callId, from)` | `call.received` event; `POST /messaging/voip/calls/{id}/reject`. Polymorfa also places and answers calls | more | `calls/server`, `calls/how-calls-work` |
| `sock.ev` callbacks in the process | One signed webhook endpoint with a delivery log | more | `development/webhooks` |
| `getMessage` store for retries | Not needed: Polymorfa runs the socket | more | none |

## Webhooks

Baileys has no webhooks. Events are in-process callbacks, so a crash loses what arrives while the process is down. Polymorfa sends the events the user picks to one signed endpoint. `X-Webhook-Signature` is HMAC-SHA256 over the raw body in lowercase hex. A failed delivery is retried up to 8 times over 24 hours, and the delivery log supports replay. See `development/webhooks`.

| Baileys event | Polymorfa event |
| --- | --- |
| `messages.upsert` | `message.received`, plus `message.reaction`, `message.vote`, `message.edited`, `message.revoked` |
| `messages.update` | `message.ack`, `message.failed` |
| `connection.update` | `connection.connected`, `connection.status`, `connection.logged_out` |
| `groups.update`, `group-participants.update` | `group.update`, `group.participant` |
| `presence.update` | `presence.update` |
| `call` | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended` |

## Differences to agree with the user

- Baileys JIDs (`@s.whatsapp.net`, `@lid`, `@g.us`, `@newsletter`) and message keys do not carry over. Polymorfa ids are opaque strings. After the Connection is up, list groups and contacts again and store the new ids. See `messaging/ids`.
- Outside Campaigns, a Connection cannot start a chat with someone who never wrote to it. Find outbound-first sends and agree a replacement, or move them to a campaign.
- Polymorfa does not queue sends while a Connection is disconnected: it refuses with `connection_not_ready`. Keep an outbox and retry with the same `Idempotency-Key`.
- Add an `Idempotency-Key` header to every send.
- Polymorfa enforces warm-up and throughput limits. Respect `Retry-After` on a `429`.
- Status updates, group join requests, GIF, video note, view-once and pin sends are not offered yet. Find code that uses them.
- Baileys 7.x is ESM-only and version 8 changes the auth state format. Do not convert the auth state by hand: import the session as it is.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Baileys handlers and verify signatures.
3. Put sending behind one adapter, so each number switches by configuration.
4. For each number, import the session (or pair through QuickLink), with Baileys offline.
5. Switch that number's traffic, watch `message.ack` and `message.failed`, then move the next number.
6. Remove the Baileys process, its auth store and its `getMessage` store only after the number runs on Polymorfa.
