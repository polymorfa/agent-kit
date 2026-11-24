# Z-API reference for polymorfa-migrate

Maps Z-API (https://developer.z-api.io) to Polymorfa. Checked on 23 November 2026 against Z-API's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `messaging/send` is https://docs.polymorfa.com/messaging/send.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/z-api.

## Mapping

### 1.1 Instance lifecycle and pairing

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Create instance (panel, or partner `POST /instances/integrator/on-demand`) | Create a QuickLink: `POST /messaging/quicklinks`; the Connection exists as soon as the link is created and its ID is returned as `data.connection`. Console: Connections > New connection. Direct creation is retired (`410 resource_gone`). | different | `connections/quicklink` |
| `GET /qr-code` (bytes) and `GET /qr-code/image` (base64) | `GET /messaging/{connection}/pair/qr`. JSON `data.qr` (string to render) or `?format=image` for a PNG. Needs direct-pairing access for the team, else `403` pointing to QuickLink. | different | `connections/direct-pairing` |
| `GET /phone-code/{phone}` | `POST /messaging/{connection}/pair/code` body `{"phone":"+15550001111"}`, code in `data.code`. Same access gate. | same | `connections/direct-pairing` |
| Passkey challenge: `POST /passkey-prologue`, `POST /reset-passkey-challenge` | `POST /messaging/{connection}/passkey/challenge` (single-use ticket), `GET.../passkey/challenge/{ticketId}`, `POST.../passkey/assertion`, `POST.../passkey/confirmation`, `GET.../passkey/confirmation`; extension ticket check `POST /passkey/verify`. QuickLink also has `POST /quicklink/{token}/passkey` and `/passkey/confirmation`. | different | `api-reference/passkey/*` |
| `GET /extension-token`, Chrome "Z-API Conector" extension | Polymorfa Connect extension (Chromium MV3 passkey worker) tied to the passkey ticket flow above. No documented "import from WhatsApp Web" token. | different | not documented in  |
| `GET /sdk-connector-token` + Connection SDK modal (`ZAPIConnector.open`) | QuickLink hosted page (`https://www.polymorfa.com/connect/...`), optionally branded; for multi-tenant, Customer pairing links `POST /platform/customers/{customerId}/pairing-links`. No embeddable JS modal found. | different | `connections/quicklink`, `customers/pairing-links` |
| `GET /status` (`connected`, `smartphoneConnected`, `error`) | `GET /platform/connections/{connectionId}` (`status` = `CONNECTING`/`CONNECTED`/`DISCONNECTED`, `statusReason`); `GET /platform/connections` to list; push via `connection.status`, `connection.connected`. | more | `connections/manage` |
| `GET /restart` | `POST /platform/connections/{connectionId}/restart` (also `messaging.connections.restart`). Returns `202` with an `operationId`; poll `GET /platform/operations/{id}` or wait for `connection.status`. | same | `connections/manage` |
| `GET /disconnect` (phone removed, webhooks stop) | `POST /platform/connections/{connectionId}/logout` unlinks the phone (`202`, async). `POST.../stop` pauses without unlinking. Re-pair needed after logout. | same | `connections/manage` |
| `GET /me` (instance data, webhook URLs, settings) | `GET /platform/connections/{connectionId}` (config), `GET /platform/connections/{connectionId}/me` (connected account), `GET /messaging/{connection}/profile`; webhooks are separate resources (`GET /platform/projects/{projectId}/webhooks`). | different | `connections/manage` |
| `GET /device` (device info) | Connected account `phonePlatform`/`accountType` on `connection.connected`; `GET /platform/connections/{connectionId}/capabilities`. A contact's linked devices: `GET /messaging/{connection}/contacts/{contactId}/devices`. Equivalent for the own phone's model/OS: not verified. | different | `connections/capabilities` |
| `PUT /update-name` (rename instance) | No public rename found in `PlatformAccessUpdateConnectionRequest` (only `configuration` and `revision`). Console rename: not verified. | gap (public API) | none |
| Delete instance (partner `DELETE /integrator/on-demand/delete`, batch delete) | `DELETE /platform/connections/{connectionId}`; bulk `POST /platform/connections/delete` and `POST /platform/connections/stop` (up to 100). | same | `connections/manage` |
| `PUT /update-auto-read-message` | Safe Mode `reads`: `replied_chats` or `all_inbound` (4 to 25 s delay, individual chats only). Needs Standard or Pro tier. Off by default. | different | `safety/safe-mode` |
| `PUT /update-auto-read-status` | No Status feature. | gap | none |
| `PUT /profile-picture`, `/profile-name`, `/profile-description` | `PUT /messaging/{connection}/profile/picture` (+ `DELETE`), `PUT.../profile/name`, `PUT.../profile/status` (the "about" text). | same | `api-reference/privacy/*`, `messaging/contacts-and-groups` |
| `PUT /update-call-reject-auto`, `/update-call-reject-message` | `PUT /platform/connections/{connection}/call-settings` with `callsEnabled:false` declines every incoming call (you still get `call.received` then `call.rejected`). Per-call: `POST /messaging/{connection}/calls/{callId}/reject`. A custom reject message: not offered. | different | `calls/server` |
| `PUT /update-announcement-guard` (scam guard for announcement groups) | Not offered. | gap | none |
| Mobile instances: `/mobile/*` registration (check availability, request code, captcha, confirm code, PIN, account email, unbanning, device transfer) | Not offered. Polymorfa only joins as a linked device or uses Cloud API. For Cloud API numbers, the Graph API has `request_code`, `verify_code`, `register`, `deregister`. | gap (different for Cloud API) | `connections/cloud-api-setup` |
| Instance queue settings `PUT /update-queue-settings` | No queue (see 1.12). | gap | none |

### 1.2 Sending, by message type

All sends are `POST /messaging/{connection}/messages/send` with `{conversation, content:{<one kind>}, quotedMessage?, mentions?, isForwarded?}` (see `messaging/send`). Response: Polymorfa `id`, `whatsapp_ids`, `conversation`, `timestamp`, `type`, `content`, `status`. Graph API equivalent: `POST /graph/whatsapp/{version}/{phoneNumberId}/messages` (Meta request shape).

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `/send-text` | `content.text` | same | `messaging/send` |
| Reply (`messageId` on send-text and media) | `quotedMessage:{id}` (Polymorfa message ID) | same | `messaging/send` |
| Mentions (`mentioned`, mention all, mention group) | `mentions:[<user id>]` (max 256 IDs, Polymorfa user IDs not numbers). No "mention all" shortcut found. | different | `messaging/send` |
| Forward (`/forward-message` by message id) | `isForwarded:true` marks a new send as forwarded. No "forward this stored message to chat X" endpoint. Not on Graph. | different | `messaging/send` |
| `/send-image` (+ `viewOnce`) | `content.image` (`url` or `base64`, `caption`, `quality: standard | hd`; HD pairs "not sent yet"). No view-once flag found. | `messaging/send`, `messaging/media` |
| `/send-video` | `content.video` (`url`/`base64`, `caption`, `thumbnail`) | same | `messaging/send` |
| `/send-audio` (`waveform`, `viewOnce`, `async`) | `content.voice` with `ptt:true` for a voice note. Waveform is read on receive (`waveform` field), not set on send. | same | `messaging/send` |
| `/send-document/{extension}` | `content.file` (`url`/`base64`, `filename`, `caption`, `mimeType`). No extension in path. | same | `messaging/send` |
| `/send-sticker` | `content.sticker` (`url`/`base64`, `emojis`, `accessibilityLabel`); `content.stickerPack`. Sticker packs and account sticker updates are release candidate, API version `2026-11-10`, unavailable in staging and production. Static sticker send itself is in `2026-09-22` spec. | more (candidate) | `messaging/stickers` |
| `/send-gif` | No GIF kind. Send an MP4 as `content.video`. `gifPlayback` flag: not found. | gap | none |
| `/send-ptv` (circular video) | Not offered. | gap | none |
| `/send-link` (link with preview) | No send-side `linkPreview` field. Put the URL in `content.text`. Received messages carry `linkPreview` (`url`, `title`, `description`, `thumbnail`). | different | `messaging/media` |
| `/send-location` | `content.location:{lat,long,address}` | same | `messaging/send` |
| `/send-contact`, `/send-contacts` | `content.contact:{vcard}`. Multiple cards: one request per card; multi-contact message: not verified. | same | `messaging/send` |
| `/send-product`, `/send-catalog` (catalog link) | `content.product`, `content.productList` (needs `businessOwnerId`; Business App Connections). Linked-device Graph catalog sends return `131026`. Plain catalog link message: not found. | more | `messaging/send`, `connections/catalog` |
| `/send-order`, `/order-status-update`, `/order-payment-update` | `content.order` (send). Order lookup `POST /messaging/{connection}/business/orders/{orderId}/lookup`. No status or payment update message. | different | `connections/catalog` |
| `/send-button-actions` (CALL, URL, REPLY) | `content.buttons` with `type: reply | url | `messaging/send` |
| `/send-button-list` (+ image, + video) | `content.buttons` with `media:{type:image | video | `messaging/send` |
| `/send-option-list` | `content.list` (sections, up to 30 rows total, unique row IDs) | same | `messaging/send` |
| `/send-button-otp` (copy code) | `content.buttons` with a `copy` control (linked device). OTP authentication templates are Cloud API (`content.template`); they are not delivered to a BSUID. | same | `messaging/send`, `messaging/templates` |
| `/send-button-pix` (PIX key + copy) | No PIX button kind. Closest: `copy` button carrying the PIX key. Native PIX payment button: not found. | different | `messaging/send` |
| `/send-carousel` | `content.carousel` (2 to 10 cards, each one image or video plus buttons; 50 MiB combined). Cloud API needs a template. | same | `messaging/send` |
| `/send-poll` | `content.poll:{title, options (2-12), multiSelect}` | same | `messaging/send` |
| `/send-poll-vote` | Not offered. Incoming votes arrive as `message.vote`. | gap | `api-events` |
| `/send-event`, `/send-edit-event`, `/send-event-response` | Not offered. | gap | none |
| `/send-newsletter-admin-invite` | Not offered. | gap | none |
| Templates (Z-API has none, `Z-API vs Official API`) | `content.template` plus template CRUD, preview, submit. Adds Meta-approved templates, Cloud API only. | more | `messaging/templates` |
| WhatsApp Flows (not in Z-API) | `content.flow`, `GET/POST /platform/flows` drafts | more | `messaging/flows` |
| Address request, phone-number request, call-permission request (not in Z-API) | `content.addressMessage`, `content.requestPhoneNumber`, `content.callPermissionRequest` | more | `messaging/send` |
| `delayMessage`, `delayTyping` (per request) | No per-request field. Use Safe Mode (`typing`, `pacing`) or `POST /messaging/{connection}/messages/typing` before a send. See 4. | different | `safety/safe-mode` |
| `async` on audio/video | `Prefer: respond-async` header on any linked-device send returns `202`; result arrives as `command.result`. | more | `messaging/send` |
| Idempotency (not in Z-API) | `Idempotency-Key` header, 1-hour receipt | more | `api/idempotent-requests` |
| Bulk and scheduled sends | Campaigns: `POST /messaging/projects/{projectSlug}/campaigns`, `/platform/campaigns` (launch, pause, reschedule, audiences, opt-outs, A/B). Pro tier. | more | `campaigns/*` |

### 1.3 Message actions

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Edit (`editMessageId`, `editImageMessageId`,...) | `PUT /messaging/{connection}/chats/{conversation}/messages/{messageId}` (scope `chats:manage`). Linked device only. | same | `messaging/send` |
| `DELETE /messages` (`owner`, `deleteForMe`) | `DELETE /messaging/{connection}/chats/{conversation}/messages/{messageId}` (revoke). Delete-for-me variant: not verified. | same | `messaging/send` |
| `/send-reaction`, `/send-remove-reaction` | `POST /messaging/{connection}/messages/react` (empty reaction clears, per channel docs; for chats not verified). Graph: `type: reaction`. | same | `messaging/send` |
| `/read-message` | `POST /messaging/{connection}/messages/seen` | same | `messaging/send` |
| (typing indicator, via `delayTyping`) | `POST /messaging/{connection}/messages/typing` with `state: typing | recording | `messaging/send` |
| Star message (not in Z-API) | `POST /messaging/{connection}/messages/star` | more | `messaging/send` |
| `/pin-message` | Not offered. | gap | none |
| Reply to button / action button / option list (`/reply-button`, `/reply-template-button`, `/reply-option-list`) | Not offered. Receive choices as `message.received` types `button_reply`, `list_reply`, `native_flow_response` with `replyChoice.id`. | gap | `messaging/receive` |
| Read stored message / media | `GET.../chats/{conversation}/messages/{messageId}`, `GET.../messages/{messageId}/media` (hosted message storage only) | more | `messaging/history` |

### 1.4 Groups

Group IDs are opaque decimals, not `...-group` or `@g.us`  pattern `^[1-9][0-9]{0,18}$`).

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /groups` (paged) | `GET /messaging/{connection}/groups` | same | `messaging/contacts-and-groups` |
| `POST /create-group` | `POST /messaging/{connection}/groups` `{name, participants:[user id] (1-256)}`. Number-only participants not accepted: resolve to a user ID first (`/contacts/check`, `/identities/resolve`). BanSafe can refuse (`bansafe_cold_blocked` applies to adding a non-contact). | same | `messaging/contacts-and-groups` |
| `/update-group-name`, `/update-group-description` | `PUT.../groups/{id}/subject`, `PUT.../groups/{id}/description` | same | same |
| `/update-group-photo` | `PUT.../groups/{id}/picture` | same | same |
| `/add-participant`, `/remove-participant` | `POST.../groups/{id}/participants/add`, `.../participants/remove` | same | same |
| `/add-admin`, `/remove-admin` | `POST.../groups/{id}/admin/promote`, `.../admin/demote` | same | same |
| `/leave-group` | `POST.../groups/{id}/leave` (and `DELETE.../groups/{id}`) | same | same |
| `/group-metadata/{phone}`, `/light-group-metadata/{phone}` | `GET.../groups/{id}` (participants included), `GET.../groups/{id}/participants`, `GET.../groups/{id}/capabilities` | same | same |
| `/group-invitation-metadata` | `GET.../groups/join-info?code=` | same | same |
| `/accept-invite-group` | `POST.../groups/join` | same | same |
| `/group-invitation-link/{groupId}`, `/redefine-invitation-link/{groupId}` | `GET.../groups/{id}/invite-code`, `POST.../groups/{id}/invite-code/revoke` (returns a new code) | same | same |
| `/update-group-settings` | Four separate PUTs: `settings/info-edit`, `settings/messages`, `settings/member-add` (`admin_add` or `all_member_add`), `settings/join-approval` | same | `messaging/linked-device-controls` |
| `/approve-participant`, `/reject-participant` (join requests) | Not offered. | gap | `messaging/contacts-and-groups` |
| Group webhooks (create, subject, description, icon, participants, join approvals) | `group.update` (`id`, `newSubject`, `newDescription`, `action`), `group.participant` (`joined`, `left`, `promoted`, `demoted`). No icon-change, invite-link-change, suspended or growth-lock events found. | different | `api-events` |
| Hybrid Connections | Group operations use the linked-device half; fail with `hybrid_group_linked_devices_unavailable` if it is down. | n/a (new) | `messaging/contacts-and-groups` |

### 1.5 Communities

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `/communities` (create, list, metadata, link, unlink, settings, deactivate, invite link, participants, admins, description) | No endpoints. The word appears only as a capability limit `communities.maxGroups` (Connection capabilities). Groups that belong to a community can still be messaged as groups. | gap | none |
| Mention group related to a community | Not offered. | gap | none |

### 1.6 Channels (newsletters)

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /create-newsletter` | `POST /messaging/{connection}/channels` | same | `messaging/channels` |
| `DELETE /delete-newsletter` | `DELETE.../channels/{id}` (returns only after WhatsApp confirms `DELETED`) | same | `messaging/channels` |
| `PUT /follow-newsletter`, `/unfollow-newsletter`, `/mute-newsletter`, `/unmute-newsletter` | `POST.../channels/{id}/follow | unfollow | `messaging/channels` |
| `GET /newsletter` (list), `GET /newsletter/metadata/{id}` | `GET.../channels`, `GET.../channels/{id}` | same | `messaging/channels` |
| Send to a channel (`phone:...@newsletter` on send endpoints) | Not documented. Channel endpoints cover read, react, view, live updates. Whether `conversation.id` of a channel is accepted by `messages/send`: not verified. | not verified (likely gap) | `messaging/channels` |
| `/update-newsletter-name`, `-description`, `-picture`, `POST /newsletter/settings/{id}` | Not offered. | gap | none |
| `/search-newsletter` | Not offered. | gap | none |
| `/newsletter/subscribers/{id}` | Not offered; `Channel.followers` is a count. | gap | none |
| Admin invite, accept, revoke, remove admin, transfer ownership | Not offered. | gap | none |
| Channel notifications | `newsletter.update` (join, leave, mute, `live_update` with view/reaction counts, `milestone`). Extras: `GET.../channels/{id}/messages`, `/message-updates`, `POST.../messages/{messageId}/viewed`, `/reaction`, `POST.../live-updates`. | more | `messaging/channels` |

### 1.7 Broadcast lists (Z-API "Transmission List")

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST/PUT/GET/DELETE /broadcast`, `...@broadcast` as `phone` | Not offered. Safe Mode text says typing indicators are never sent to "broadcast lists". Replacement: Campaigns plus Audiences (`/platform/audiences`, members, segments), which send individual messages and respect opt-outs. | gap (different tool) | `campaigns/*` |

### 1.8 Status (stories)

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `/send-text-status`, `/send-image-status`, `/send-video-status` | Not offered. | gap | none |
| `/reply-status-text`, `/reply-status-gif`, `/reply-status-sticker`; `isStatusReply` | Not offered. | gap | none |

### 1.9 Contacts

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /contacts` (paged) | `GET /messaging/{connection}/contacts` | same | `messaging/contacts-and-groups` |
| `GET /contacts/{phone}` | `GET.../contacts/{contactId}` (stable ID), `GET.../contacts/{contactId}/info` (live) | same | `messaging/user-identities` |
| `GET /profile-picture` | `GET.../contacts/{contactId}/picture` | same | same |
| `GET /phone-exists/{phone}`, `POST /phone-exists-batch` (max 50,000) | `GET.../contacts/check?phone=` (one or a list, max 1,000). Returns `exists`, `id`, `phoneNumber`. Also `GET.../identities/resolve?phoneNumber= | username= | `messaging/user-identities` |
| `@lid` lookup (number to lid) | Not needed: the stable `id` replaces both. | different | `messaging/user-identities` |
| `POST /contacts/modify-blocked` | `POST.../contacts/{contactId}/block`, `/unblock`, `GET.../contacts/blocked`; event `blocklist.update` | same | `messaging/user-identities` |
| `GET /privacy/disallowed-contacts` | Privacy categories with `contact_allowlist`/`contact_blacklist` values; the actual lists: not verified | different | `messaging/linked-device-controls` |
| `POST /contacts/add`, `DELETE /contacts/remove` (phone address book) | Not offered. | gap | none |
| `POST /contacts/{phone}/report` | Not offered. | gap | none |
| Business profile of a contact | `GET.../contacts/{contactId}/business-profile` | more | `messaging/linked-device-controls` |
| Identity verification code (not in Z-API) | `GET.../users/{id}/security-code` | more | `messaging/user-identities` |

### 1.10 Chats

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /chats`, `GET /chats/{phone}` | `GET.../chats`, `GET.../chats/{conversation}`, `GET.../chats/{conversation}/messages`. Requires hosted message storage on for the Connection (beta); expires by retention. | different | `messaging/history` |
| `/modify-chat` `archive | unarchive` | `POST.../chats/{conversation}/archive | `messaging/send` |
| `/modify-chat` `read | unread` | `POST.../messages/seen` for read. Mark unread: not found. Event `chat.read`. | `messaging/send` |
| `/modify-chat` `pin | unpin`, `mute | unmute`, `clear`, `delete` | `api-events` |
| `/send-chat-expiration` | `PUT.../chats/{conversation}/disappearing` `{durationSeconds: 0 | 86400 | `messaging/linked-device-controls` |
| Chat presence (`PresenceChatCallback`) | `presence.update`; subscribe `POST.../presence/{conversation}/subscribe` (120 s), read `GET.../presence/{conversation}`. Off unless the project enables `presenceMode`. | more | `messaging/linked-device-controls` |

### 1.11 Labels, tags and notes

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /tags`, create, edit, delete tag, tag colors | `GET/POST /messaging/{connection}/labels`, `PUT/DELETE.../labels/{labelId}`. Color is a field on the label. Needs `labels:manage`; observation `labelMode` must be on for reads. | same | `messaging/linked-device-controls` |
| `PUT /chats/{phone}/tags/{tag}/add | remove` | `GET/PUT.../labels/chats/{conversation}` (PUT replaces the full set; empty array removes all). Not an add/remove pair: read-modify-write. | same |
| `POST /chats/{phone}/notes` | Not offered. | gap | none |
| Label webhooks (chat label association) | `labels.update` (`label_edit`, association, star) | same | `api-events` |

### 1.12 Privacy

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `/privacy/last-seen`, `photo-visualization`, `description`, `group-add`, `online`, `read-receipts`, `messages-duration` | `GET /messaging/{connection}/privacy` and `PUT /messaging/{connection}/privacy/{setting}` with `{value}`. Settings: `groupadd`, `last`, `status`, `profile`, `readreceipts`, `online`, `calladd`, `messages`, `defense`, `stickers`. Values: `all`, `contacts`, `contact_allowlist`, `contact_blacklist`, `match_last_seen`, `known`, `none`, `on_standard`, `off`. Default disappearing timer has its own PUT. | more | `messaging/linked-device-controls` |

### 1.13 Business catalog and profile (Business App Connections)

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Products: `POST /products`, `GET /products/{id}`, `DELETE /products/{id}`, `GET/POST /catalogs[/{phone}]` | `POST.../business/products`, `GET | PUT | `connections/catalog` |
| Collections (create, list, edit, delete, products add/remove) | `GET/POST.../business/collections`, `GET | PATCH | `connections/catalog` |
| Catalog of another business number (`GET /catalogs/{phone}`) | Not found on native API. Graph: `GET /graph/whatsapp/{version}/{wabaId}/product_catalogs[/{catalogId}/products]` for Cloud API. | different | `api/graph/index` |
| Company description, email, address, websites, hours, categories; `GET /business/profile`; `GET /business/available-categories` | `GET | PATCH.../business/profile` (single PATCH of description, address, email, websites, hours, categories), `PUT/DELETE.../business/profile/cover-photo`, `GET | `connections/business-profile` |
| (Quick replies, not in Z-API) | `GET | POST.../business/quick-replies`, `PUT | `connections/quick-replies` |

### 1.14 Queue and delays

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Message queue: `POST/GET /queue`, `/queue/count`, `DELETE /queue`, `DELETE /queue/{zaapId}`; queue holds up to 1,000 while disconnected, flushes on reconnect | No API queue. A send while the Connection is disconnected fails: `503 connection_not_ready` (sync) or `message.failed` `connection_not_connected` (async). Retry is the caller's job. Related: `Idempotency-Key`, the `messages_operation` MCP tool for an uncertain send, and `GET /platform/operations` for async connection operations. | gap | `api/errors` |
| `zaapId` return value | `id` (Polymorfa message ID) plus `whatsapp_ids` | different | `messaging/ids` |
| `delayMessage` (1-15 s, default random 1-3 s) | Safe Mode `pacing`: `jittered` (0.7 to 2.6 s since previous send) or `conversation` (also 2 to 15 s after the inbound message it answers). Per project ceiling and per Connection override. Standard or Pro tier. | different | `safety/safe-mode` |
| `delayTyping` (1-15 s) | Safe Mode `typing`: `before_text` or `before_all` (about 4.2 chars per second, 0.9 to 9 s; recording indicator for voice notes 2.5 to 4 s). Never to groups, channels, bots or broadcast lists. Or call `messages/typing` yourself. | different | `safety/safe-mode` |
| Warm-up and throughput guard (advice only in Z-API) | Enforced: warm-up plan, daily allowance, `bansafe_throttled`, `bansafe_daily_allowance_reached`, cold-send block, new-chat cap | more | `safety/warm-up-plan`, `connections/new-chat-cap` |

### 1.15 Webhooks (configuration)

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Seven `PUT /update-webhook-*` setters (one URL per event kind) plus `PUT /update-every-webhooks` | One endpoint with an `eventTypes` list: `POST /platform/projects/{projectId}/webhooks` (project events) or `POST /platform/webhooks` (Customer and campaign events). Update `PATCH`, disable with `enabled:false`, delete. Many endpoints per project. The Messaging API also has `POST /messaging/webhooks` (`events`, optional customer-chosen `hmacKey`). | more | `development/webhooks` |
| HTTPS only | HTTPS public URL required (QuickStart). Local dev: CLI forwards events to localhost. | same | `development/webhooks/quickstart` |
| `PUT /update-filters` `messageFilters` (group/private/text/image/...) and `callbackTypeFilters` | Event-type subscription only. No per-message-kind or group-vs-private filter found. Pick `eventTypes`; filter in your handler. | gap (partial, via eventTypes) | `development/webhooks` |
| `PUT /update-notify-sent-by-me` | `message.received` carries `fromMe` (shown `false` in the example). Messages you send through the API arrive as `message.sent`. Messages typed on the phone: `message.echo` is documented for coexistence Connections only; for linked-device phone sends: not verified. | different | `messaging/receive` |
| Webhook test | `POST.../webhooks/{webhookId}/tests` (synthetic event, real delivery) | more | `development/webhooks` |
| Delivery log, retry, replay | `GET /platform/webhook-deliveries`, attempts, `POST.../retry`, `POST /platform/events/{eventId}/replays`, SSE `GET /platform/projects/{projectId}/events/stream` (beta) | more | `development/webhooks`, `development/event-streams` |
| Signature | Z-API: none documented. Polymorfa: HMAC-SHA256, see section 3. | more | `development/webhooks` |

### 1.16 Webhook events

See section 3 for field-level mapping.

| Z-API webhook `type` | Polymorfa event | Status |
|---|---|---|
| `ReceivedCallback` | `message.received` (+ `message.reaction`, `message.vote`, `message.edited`, `message.revoked`, `message.update`, `message.delete`, `message.echo`) | same (shape differs) |
| `DeliveryCallback` | `message.sent`, `message.failed`, and sync `4xx/5xx` errors | different |
| `MessageStatusCallback` (`SENT`, `RECEIVED`, `READ`, `READ_BY_ME`, `PLAYED`) | `message.ack` with `type: error | delivered | different |
| `PresenceChatCallback` | `presence.update` | same (opt-in) |
| `ConnectedCallback` | `connection.connected`, `connection.status` | same |
| `DisconnectedCallback` | `connection.status` (`DISCONNECTED`, `statusReason`), `connection.logged_out` (`reason: banned | device_removed | more |
| `ProxyCallback` | Not offered (no proxy). | gap |
| `notification` values: group create/subject/description/participants | `group.update`, `group.participant` | same (fewer kinds) |
| `GROUP_CHANGE_ICON`, `GROUP_CHANGE_INVITE_LINK`, `GROUP_SUSPENDED/UNSUSPENDED`, `GROUP_GROWTH_LOCKED/UNLOCKED`, join-request notifications | Not found | gap |
| `CALL_MISSED_VOICE/VIDEO`, call received/accepted/ended | `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended`, `call.telemetry`, `call.participant_*`, `call.connection_*`, `call.permission_changed`. `hasVideo` on `call.received`. | more |
| `REVOKE` | `message.revoked`, `message.delete` | same |
| `BIZ_MOVE_TO_CONSUMER_APP`, `BLUE_, `E2E_ENCRYPTED`, `CIPHERTEXT`, `WA_OLD_REGISTRATION` | No equivalent found. | gap |
| `errorCode SHADOW_BAN`, `REACHOUT_TIMELOCKED`, `NEW_CHAT_MESSAGES_CAPPED` | `connection.restriction_updated` (`reachout_timelock`), `new_chat_limit_reached` error code, `bansafe.incident`, `bansafe.health_threshold`, `bansafe.action` | more |
| Profile name/picture update, chat label association notifications | `contact.update`, `labels.update`, `contact.sync` | same |
| Channel admin invite/promotion notifications | `newsletter.update` covers join/leave/mute/live/milestone, not admin changes | gap |

### 1.17 Security and auth

| Z-API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Instance id + token in the URL; `Client-Token` header | `Authorization: Bearer <credential>`. Credentials: team key `pmfa_`, project token `pmfa_pt_`, client token `pmfa_ct_`. Connection ID in the path, never a secret. See section 2. | different | `api/authentication` |
| Scoped access | Per-key scopes (`messages:write`, `connections:manage`,...), project confinement, expiry 30/90/365 days, service accounts, rotation, revocation. | more | `development/api-keys` |
| Account IP allowlist (panel) | Not found for API keys. Client tokens have `allowedOrigins`, `rateLimit`, `maxDaily`, `recipientMode`. | gap | `development/client-tokens` |
| Browser-safe access (Z-API: "never expose id/token") | Short-lived client tokens `POST /platform/client-tokens`, one Connection, action allowlist | more | `development/client-tokens` |
| Panel 2FA | Account security (passkeys, 2FA) for Console login | same | `teams/account-security` |
| Rate limit: "no limit" | Team request quota (`429`, `Retry-After`, `X-RateLimit-*`) plus WhatsApp-side limits | different | `api/rate-limits` |
| Audit | Audit logs `GET /platform/audit`, request logs | more | `development/request-logs` |

### 1.18 Partner API (multi-tenant)

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Create / list / update / cancel / delete instances with `Partner-Token` | Customers API: `POST /platform/customers`, `GET /platform/customers/{id}/connections`, archive/restore, pairing links, connection transfer, per-Customer shared monthly cap. Billing is per online Connection-day, no instance subscription lifecycle. | different | `customers/*` |
| Subscribe / cancel subscription | Not applicable: Connection tier changes `POST /platform/connections/{id}/tier-quotes`, `PATCH /platform/connections/{id}` | different | `billing/connection-tiers` |
| `withCalls` upgrade | Call settings plus plan allowance | different | `calls` |
| 2-day trial | Free team: 1 project, 1 real Connection; test Connections cost 0 credits | different | `testing/test-connections` |
| Connect modal / white label | Branded QuickLink (paid add-on) | different | `connections/quicklink` |

### 1.19 Proxy

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `PUT /integrator/configure-proxy`, `PUT /update-proxy-webhook`, `ProxyCallback` | Not offered. | gap | none |

### 1.20 Calls

| Z-API capability and endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /send-call` (ring then hang up, max 15 s, optional audio URL) | `POST /messaging/voip/calls` places a real call. Pre-check `POST /messaging/voip/calls/check`. No fixed ring-and-hang-up mode; end with `DELETE /messaging/voip/calls/{id}`. | different | `calls/server` |
| Call SDK `@z-api/call` + `GET /call-token` | Browser: client tokens with `voip_*` actions plus call components (React and web component, prerelease). Server: `@polymorfa/sdk` `messaging.voip` and `CallsClient` over the media socket (speak and listen). | more | `calls/web`, `calls/server` |
| SIP: `POST /sip-token`, `GET /sip-info`; `sip.z-api.io` | `GET /platform/sip/endpoint` (address), SIP trunk CRUD `POST/PATCH/DELETE /platform/sip-trunks`, credential rotation `POST /platform/sip-trunks/{id}/credentials`. Both directions (inbound ring your PBX, outbound from your PBX). | more | `calls/sip-trunks` |
| Up to 3 simultaneous calls | `simultaneousCalls` in call settings; group calls with participants, waiting room | more | `calls/server` |
| Call events (inside `ReceivedCallback`) | Dedicated events, see 1.16 | more | `calls/how-calls-work` |
| (not in Z-API) call permission, do-not-call list, blocked country codes, records, retention, TTS audio assets | `/platform/call-opt-outs`, `/platform/call-policy`, `/platform/calls`, `/platform/voice/audio*` (Voice Automation, needs access) | more | `calls/permissions`, `calls/records` |

### 1.21 MCP

| Z-API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `https://mcp.z-api.io/mcp`, OAuth, 9 tools (send text/image/video, group create/add/remove/admin/metadata) | `https://api.polymorfa.com/mcp`, Streamable HTTP, Bearer credential (team key, project token with `mcp` scope, or client token with `mcp` action), no OAuth. Tool families: connections, messages and chats, groups, contacts, channels, presence/profile, labels, webhooks, history, events, operations, media, account management. | more | `development/mcp` |
| MCP cannot pair | Correct on both sides. Polymorfa MCP cannot return QR or pairing codes; use QuickLink. | n/a | `development/mcp` |

### 1.22 Meta AI

| Z-API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Chat with Meta AI via `/send-text` to `13135550002` | Not documented as a feature. `metaAi` is a read-only capability flag (WhatsApp enabled Meta AI for the connection). Whether a send to that number works: not verified. | gap (not verified) | `connections/capabilities` |

### 1.23 Integrations and SDKs

| Z-API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Postman collection; REST docs | OpenAPI 3.1 specs (Messaging, Platform, Graph) in the API reference; interactive playground | more | `api/overview` |
| SDKs: none for REST (only `@z-api/call`, Connection SDK) | `@polymorfa/sdk` (TypeScript, npm prerelease). For other languages call the HTTP API. | more (TypeScript) | `get-started/development-environment` |
| Find My Pack integration | None. | gap | none |
| Zapier hint (`id` field "for Zapier compatibility") | No documented n8n, Make, Zapier or Pipedream integration. Call the API from those tools over HTTP. | different | `api/overview` |
| Meta-format webhooks and Graph API (Z-API has none) | `format:"meta"` webhooks (`X-Hub-Signature-256`), `/graph/whatsapp/{version}/...` | more | `api/graph/index` |

### 1.24 Media

| Z-API capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Send by public URL or data-URI base64 | `url` or raw `base64` field per kind (no `data:` prefix documented; exactly one of url, base64, descriptor) | same | `messaging/send` |
| Received media URL on Z-API storage for 30 days | No hosted copy. Events carry a `media` reference; download with `GET /messaging/media/{id}` or `GET.../chats/{conversation}/messages/{messageId}/media` (media:read). Persist yourself or `POST /messaging/media/{id}/download-and-save` to your S3. Hosted message storage keeps only type, caption, MIME type. | different | `messaging/media`, `messaging/history` |
| Media upload | `POST /messaging/{connection}/media/uploads`, `/media/upload-grants` | more | `messaging/media` |

---

## 2. Auth and identifiers

### 2.1 Credentials

| Z-API | Polymorfa | Notes |
|---|---|---|
| Instance ID (URL path) | Connection ID (URL path, opaque decimal string, e.g. `739182640518203`). Platform paths also accept the Connection UUID or slug (`/platform/connections/sales-1/safe-mode`). | Not a secret. Created by QuickLink (`data.connection`), listed by `GET /platform/connections`. |
| Instance token (URL path secret) | No per-connection secret. Access comes from a credential. | One Z-API token per number becomes one credential per scope of access. |
| `Client-Token` header (account-level, optional) | `Authorization: Bearer <team key or project token>`. Team key `pmfa_...` (all projects) maps to Client-Token. Project token `pmfa_pt_...` (one project) is the least-privilege replacement for a per-instance token. | Created only in the Console (Settings > API Keys); no API creates them. Scopes required per method. |
| (browser exposure) | Client token `pmfa_ct_...`, minted by your server via `POST /platform/client-tokens`, one Connection, action allowlist, TTL. | Needs the issuing credential to hold `connections:manage`, `messages:write`, `contacts:read`, `presence:read`, `presence:observe`, `mcp`. |
| `Authorization: Bearer <Partner-Token>` | Team key plus Customers API. | See 1.18. |
| IP restriction | Not offered for keys. | Gap. |

A migration agent cannot mint keys. Ask the human to create a project token with scopes `messages:write`, `contacts:read`, the group, contact and chat scopes each reference page lists, `webhooks:manage`, `connections:manage`, then set `POLYMORFA_KEY`. Scope names per method are in each reference page and.

### 2.2 Phone numbers

- Z-API `phone`: digits only, `5511999999999`.
- Polymorfa `conversation.phoneNumber`: E.164 with `+` (`+5511999999999`). The Graph API `to` takes digits without `+`.
- The returned `phoneNumber` is WhatsApp's resolved phone and can differ from the input. Match conversations by `conversation.id` per Connection, not by the entered string.
- Brazil 9-digit normalization: linked-device Connections resolve phone lookups with WhatsApp before sending. Explicit statement about the extra 9: not verified.

### 2.3 Chat, group and user IDs

| Z-API id | Polymorfa |
|---|---|
| Number as chat id (`5511...`) | `conversation.phoneNumber`, or `conversation.id` (Polymorfa conversation ID). Always keep the returned `conversation.id`. |
| `999...@lid`, `chatLid`, `senderLid`, `participantLid` | Not exposed. The stable user `id` (decimal string) replaces LID and number. `phoneNumber`, `bsuid`, `username` are optional aliases and can be missing when WhatsApp hides the number. Reply to hidden-number senders with `conversation.id`. Ask for the number with `content.requestPhoneNumber` (event `phone_number_shared`). Resolve: `GET /identities/resolve?phoneNumber=|username=|id=`. |
| Group `120363019502650977-group` or `5511...-1623275280` | Group `id`: opaque decimal string (`^[1-9][0-9]{0,18}$`). No JID input is accepted. Build a map once with `GET /messaging/{connection}/groups` (match by name or participants) and store `group.id`. A Z-API group id cannot be converted. The group author on received messages is `conversation.sender`. |
| `...@newsletter` | Channel `id` (string; the schema does not constrain it to decimal, so the exact format is not verified). Use `GET /messaging/{connection}/channels` to map. Message position is a cursor (`position`), not an ID. |
| `...@broadcast` | No equivalent. |
| `messageId` (WhatsApp) and `zaapId` | Polymorfa message `id` (opaque decimal) for all actions. WhatsApp's id is in `whatsapp_ids.linked_devices` (or `official_api`). Do not pass the WhatsApp id where `id` is expected. Keep both when migrating stored threads. Polymorfa `id` is scoped to the Connection that emitted it. |
| Z-API `momment` (ms epoch) | `timestamp` Unix seconds in message payloads (Cloud API sends it as a string), ISO 8601 on the event envelope. |


---

## 3. Webhook migration

### 3.1 Transport

| Topic | Z-API | Polymorfa |
|---|---|---|
| Registration | Seven PUT setters, URL per event kind | `POST /platform/projects/{projectId}/webhooks` with `url`, `eventTypes`, `format` (`native` default or `meta`), `retryPolicy`, `enabled`, `phoneOfflineStartDay`, custom headers. Each mutation needs an `Idempotency-Key`. Needs `webhooks:manage`. |
| Method and body | `POST` JSON | `POST` JSON, `Content-Type: application/json`, `User-Agent: polymorfa-webhook/1.0` |
| Signature | None documented | `native`: header `X-Webhook-Signature: <lowercase hex>`. `meta`: header `X-Hub-Signature-256: sha256=<hex>`. Both HMAC-SHA256 over the exact raw body with the endpoint's signing secret. No timestamp header. Constant-time compare. A Messaging API webhook created without `hmacKey` is unsigned. Secret is returned once on create; rotate with `POST.../secret-rotations` (previous secret valid for `overlapSeconds`). |
| Trace headers | none | `X-Polymorfa-Delivery-ID` (same for all attempts), `X-Polymorfa-Delivery-Attempt` (starts at 1) |
| Retries | not stated | Up to 8 total attempts over 24 hours; fixed offsets 30 s, 2 min, 10 min, 1 h, 4 h, 12 h, 24 h; `retryPolicy.maximumAttempts` can lower it (project 1-10, team 0-10; `1` disables). Saved `initialDelaySeconds` and `backoff` do not change the automatic schedule. Retries on network error, timeout, `408`, `429`, `5xx`. Any other non-2xx ends the delivery. |
| Timeout | not stated | 30 s per attempt, up to 3 redirects. Respond fast, process later. |
| Idempotency | none | Event `id` is stable across retries. Dedupe on it. Delivery is at least once and unordered. |
| Redelivery | none | `POST /platform/webhook-deliveries/{id}/retry` (key required), `POST /platform/events/{eventId}/replays` |


### 3.2 Envelope

```json
{
  "id": "<event id>",
  "connection": "739182640518203",
  "timestamp": "2026-10-19T10:05:00.000Z",
  "event": "message.received",
  "payload": {... }
}
```
Z-API's `instanceId` becomes `connection`. Z-API's `type` becomes `event`. Z-API's flat fields move under `payload`.

### 3.3 `ReceivedCallback` to `message.received`

| Z-API field | Polymorfa field |
|---|---|
| `instanceId` | envelope `connection` |
| `messageId` | `payload.id` (Polymorfa). WhatsApp id in `payload.whatsapp_ids.linked_devices` |
| `phone` (chat, group or `@lid`) | `payload.conversation.id` plus `phoneNumber`/`bsuid`/`username` when known |
| `participantPhone`, `participantLid` | `payload.conversation.sender` (group messages) |
| `isGroup` | `payload.isGroup` |
| `fromMe` | `payload.fromMe` |
| `momment` | `payload.timestamp` (Unix seconds) and envelope `timestamp` |
| `senderName`, `chatName` | `payload.pushName` (Cloud API: `senderName`). Group name: not on the payload; read via `GET /groups/{id}`. |
| `senderPhoto`, `photo` | Not on payload. `GET /contacts/{contactId}/picture`. |
| `connectedPhone` | `connection.connected.payload.phoneNumber`; not repeated per message. |
| `referenceMessageId` (reply target) | `payload.parentMessageId` |
| `forwarded` | not found on `MessagePayload` |
| `status` (`PENDING`...`PLAYED`) | not on received payloads; use `message.ack` for your sends |
| `isEdit` | `message.edited` event, `payload.edited`, `type: "edited"` |
| `isNewsletter` | `newsletter.update` |
| `isStatusReply`, `broadcast`, `waitingMessage` | no equivalent |
| `expiresAt`, `messageExpirationSeconds` | not found on the payload |
| `externalAdReply` | Cloud API `referral` (entry point) |

Content key mapping (Z-API puts one extra top-level key; Polymorfa uses `payload.type` plus type fields):

| Z-API content key | Polymorfa `payload.type` and fields |
|---|---|
| `text` | `text`, `payload.text`; `linkPreview` for URL cards |
| `image`, `video`, `audio`, `document`, `sticker` | `image`, `video`, `audio` (`ptt`, `waveform`, `seconds`), `document` (`filename`, `pageCount`), `sticker`; `caption`, `mimeType`, `width`, `height`, `thumbnail`, `media` (download reference). No Z-API-style 30-day public URL (`mediaUrl` exists on `MessagePayload`; lifetime not verified). HD copy: `association.parentMessageId`, `quality`. |
| `location` | `location`: `latitude`, `longitude`, `displayName` |
| `contact` | `contact` (vcard) |
| `reaction` | `message.reaction` event or `type: reaction` (`reaction`, `reactionTo`) |
| `poll` / `pollVote` | `poll` (`pollOptions`) / `message.vote` (`pollMessageId`, `voter`, `selectedHashes`) |
| `buttonsResponseMessage`, `listResponseMessage`, `hydratedTemplate` reply | `button_reply`, `list_reply`, `native_flow_response`; match on `replyChoice.id` |
| `buttonsMessage`, `carouselMessage` (as received) | not delivered as rich types; `unknown` |
| `product`, `order`, `reviewOrder`, `reviewAndPay`, `requestPayment`, `sendPayment` | Cloud API `order` object; others: not found |
| `pinMessage`, `event`, `eventResponse`, `newsletterAdminInvite`, `pixKeyMessage`, `statusImage|Video|Audio`, `broadcastRecipients`, `viewOnce` | no equivalent |
| `notification` (group/call/etc.) | see 1.16 |

`type` values on `message.received`: `text`, `image`, `video`, `audio`, `document`, `location`, `contact`, `phone_number_shared`, `native_flow_response`, `button_reply`, `list_reply`, `poll`, `sticker`, `sticker_pack`, `reaction`, `revoke`, `edited`, `unknown`.

### 3.4 Other Z-API webhooks

| Z-API | Polymorfa | Field notes |
|---|---|---|
| `DeliveryCallback` (`phone`, `zaapId`, `messageId`, `error`, `errorCode`) | `message.sent` (success: `id`, `whatsapp_ids`, `conversation`, `type`, `timestamp`); `message.failed` (`to`, `type`, `error`: `invalid_recipient`, `connection_not_connected`, `ack_timeout`, `send_failed`, `blocked_by_safety`; `code`; `retryAfter`) | `message.failed` is the async path (`Prefer: respond-async`) and for post-accept failures. Sync errors return as the HTTP response with a stable `error.code`. |
| `MessageStatusCallback` `RECEIVED` / `READ` / `PLAYED` | `message.ack` `type: delivered` / `read` / `played`, `messages:[{id, whatsapp_ids}]`, `conversation`, `from`, `timestamp`, optional `pricing` | `ids[]` becomes `messages[]`. `error` ack type has no Z-API twin. `SENT` -> `message.sent`. `READ_BY_ME` -> not found. |
| `PresenceChatCallback` (`AVAILABLE`, `COMPOSING`, `RECORDING`, `PAUSED`, `UNAVAILABLE`) | `presence.update` (`from`, `state`, `lastSeen`, `observedAt`) | Needs `presenceMode`/`typingMode` set to `events` or `cache` first. Off by default. |
| `ConnectedCallback` (`connected`, `phone`) | `connection.connected` (`phoneNumber`, `id`, `pushName`, `phonePlatform`, `accountType`, `businessName`) | |
| `DisconnectedCallback` (`error`) | `connection.status` `DISCONNECTED` with `statusReason`; `connection.logged_out` with `reason` (`banned` code 406, `device_removed` code 401, `unknown`), `code`; `TEMPORARY_BAN` adds `banCode`, `banReason`, `banExpiresAt` (Unix seconds); `connection.phone_offline` warns days 7-13 before the 14-day sign-out. | |
| `ProxyCallback` | none | |
| Group `notification`s | `group.update`, `group.participant` | |
| `CALL_*` | `call.*` | |

### 3.5 What a migrating handler must change

1. Verify `X-Webhook-Signature` on raw bytes first (new). 
2. Read `event`, not `type`; read the body under `payload`.
3. Key people by `conversation.id`; stop parsing JIDs and `@lid`.
4. Replace `messageId` with `payload.id` for actions; store `whatsapp_ids`.
5. Respond 2xx within 30 s after durable save; dedupe on envelope `id`; accept reordering.
6. Subscribe to specific `eventTypes`; there are no message-kind filters.
7. Handle new events: `message.failed`, `connection.restriction_updated`, `bansafe.*`.

---

## 4. Gaps and behaviour differences a migrating agent must handle

Gaps (not offered or not found):

1. Status and stories (send, reply, auto-read).
2. Broadcast lists (`@broadcast`). Use Campaigns or loop sends.
3. Communities (all management endpoints).
4. Channel management beyond create, delete, follow, mute, list, get, read, react (no rename, picture, description, settings, search, subscribers, admins, ownership, invites). Sending into a channel is not documented.
5. Mobile instances (primary-device registration, SMS or voice code, PIN, unban request).
6. Proxy per instance and the `ProxyCallback`.
7. GIF and PTV send kinds, view-once flag, send-side link preview, pin message, poll vote send, event messages, order status and payment updates, reply-to-button helpers, forward-by-id, chat pin, mute, clear, delete, notes, address-book add and remove, report contact, announcement-group scam guard, group join-request approve and reject (linked-device), group icon and invite-link and suspended events, per-message-kind webhook filters, account IP allowlist, custom call reject message, public instance rename, PIX button.
8. Meta AI chat: not documented.
9. Queue API and queue-on-disconnect.

Behaviour differences:

- **Queue on disconnect.** Z-API queues up to 1,000 sends while the phone is offline and flushes on reconnect. Polymorfa refuses: `503 connection_not_ready` (sync) or `message.failed` `connection_not_connected`. The migrating app needs its own outbox. Use `Idempotency-Key` (1-hour window) so a retry cannot double-send. Do not retry on `bansafe_send_outcome_unknown` or `result_unknown`; read message events first.
- **First messages to people who never wrote.** Outside Campaigns, a first message to such a contact is refused (`bansafe_cold_blocked`, `403`); adding that person to a group is also refused. Z-API sends them. Route outreach through Campaigns (Pro) or message people who wrote first.
- **Pacing is enforced, not advised.** Warm-up allowance (`bansafe_daily_allowance_reached`, `429`), throttle (`bansafe_throttled`, `429`, `Retry-After`), WhatsApp new-chat cap (`new_chat_limit_reached`, `429`). Z-API's "no limit" has no equivalent. Respect `Retry-After`.
- **Delays.** `delayMessage` and `delayTyping` per request are gone. Map them to project Safe Mode (`pacing`, `typing`, `presence`, `reads`), all off by default, Standard or Pro only, owner or admin to change. Contacts see presence, typing and read receipts, which cannot be undone.
- **Buttons.** Z-API needs a panel terms acceptance and mixes types poorly. Polymorfa linked-device buttons allow up to 10 controls and 3 CTAs; copy and catalog controls cannot mix with replies. Cloud API direct sends allow 1 to 3 replies only; richer buttons need an approved template. Capture replies as `button_reply` / `list_reply` / `native_flow_response` and key on `replyChoice.id`. Client rendering differs between Web and phones.
- **Media.** Z-API stores received media 30 days on its CDN. Polymorfa keeps no attachment files. Download on webhook receipt (or `download-and-save` to your bucket). Hosted message storage keeps type, caption and MIME only.
- **IDs.** Everything is an opaque decimal string. Do not parse, cast to number, or look for `@g.us`, `@lid`, `-group`. Remap stored Z-API group ids by listing groups.
- **Hosted history.** There is no `GET /chats` of everything the phone has. History needs hosted message storage (beta) and is bounded by retention. History-sync ingest is a separate `history.sync` event (default metadata-only).
- **Webhook shape and delivery.** Unified endpoint with event list; signed; at least once; up to 8 attempts over 24 h; 30 s timeout; unordered.
- **Cloud API Connections differ.** Edits, deletes, groups and channels are linked-device only; free-form sends outside the 24 h customer service window fail with `conversation_window_closed`; templates only; typing indicator needs an inbound message. Hybrid group operations need the linked-device side connected.
- **Async completion.** Connect, start, stop, restart and logout return `202` plus an `operationId`. Wait on `connection.status` or `GET /platform/operations/{id}` before the next step.
- **Pairing access.** Direct QR and pairing code endpoints need team access; default is QuickLink. Pairing is human-in-the-loop. MCP cannot fetch QR. Funding is checked when pairing starts.
- **Billing model.** Per online Connection-day with tiers (Free, Standard, Pro) and call allowances, not per instance per month. A stopped Connection still counts down paid time. Tier gates BanSafe Lite (Safe Mode), Campaigns, Ban Credit.
- **Calls.** `send-call` is a ring-and-hang-up on Z-API. Polymorfa places a real call and bills against the call allowance. Cold calls to people the Connection never chatted with are refused while a `reachout_timelock` restriction is active. Respect call permission and do-not-call lists.
- **Test mode.** A test Connection sends only to other active test Connections in the same project. Do not migration-test against real recipients there.

---
