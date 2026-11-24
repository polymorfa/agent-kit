# ZapLigue reference for polymorfa-migrate

Maps ZapLigue (https://www.zapligue.com, API docs at https://app.zapligue.com/docs) to Polymorfa. Checked on 24 November 2026 against ZapLigue's published site and API page and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `calls/server` is https://docs.polymorfa.com/calls/server.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/zapligue.

ZapLigue is a web app that places WhatsApp voice calls in bulk from the customer's own numbers, with recorded audio, a visual IVR builder and an ElevenLabs voice agent, and also sends message broadcasts. Its public API has eight endpoints and no webhooks. Most of what a customer uses lives in the ZapLigue panel, not in code, so the inventory step must ask the user about panel campaigns, audio files, IVR flows and agents as well as searching the repository.

## 1. Mapping

### 1.1 Credentials and conventions

| ZapLigue | Polymorfa | Status | Docs page |
| --- | --- | --- | --- |
| Base URL `https://api.zapligue.com`, routes under `/v1` | `https://api.polymorfa.com`: `/platform/...` for connections and call records, `/messaging/...` for calls and sends | different | `api/overview` |
| `x-api-key: ura_...` header, shown once at creation. The QR stream also accepts `?api_key=` | `Authorization: Bearer <API key>`. Calls need `connections:manage`; call records need `connections:read` | different | `development/api-keys` |
| Responses `{success, data}` or `{success: false, message}` | Success bodies carry `data`; errors carry `error.type`, `error.code` and `error.request_id`. Match on `error.code` | different | `api/errors` |
| Phones as digits with country code, no plus sign (`5511999990000`) | E.164 with a plus sign (`+5511999990000`) in `to` and `conversation.phoneNumber`. Do not strip or re-add the plus by hand: normalise once at the adapter | different | `calls/server` |
| Instance, campaign, AI agent and IVR flow ids (cuid strings) | Polymorfa ids are opaque strings; none carry over. Look them up again | different | `messaging/ids` |

### 1.2 Instances and pairing

| ZapLigue endpoint | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `GET /v1/instances` (id, name, status, phoneNumber, profilePictureUrl, connectedAt, createdAt) | `GET /platform/connections` (list) and `GET /platform/connections/{connectionId}` (`status` `CONNECTING`, `CONNECTED` or `DISCONNECTED`, with `statusReason`) | more | `connections/manage` |
| `POST /v1/instances/{id}/connect` | Create a QuickLink: `POST /messaging/quicklinks`. The Connection exists once the link is created and its id comes back as `data.connection` | different | `connections/quicklink` |
| `GET /v1/instances/{id}/qr/stream` (server-sent events `stream_ready`, `qr_code`, `connected`, `disconnected`) | The customer scans a QR code or enters a pairing code on the hosted QuickLink page. Direct `GET /messaging/{connection}/pair/qr` and `POST /messaging/{connection}/pair/code` need direct-pairing access for the team. Observe results through the `connection.status` and `connection.connected` webhook events | different | `connections/quicklink`, `connections/direct-pairing` |
| `POST /v1/instances/{id}/restart` | `POST /platform/connections/{connectionId}/restart`. Returns `202` with an operation id; wait for `connection.status` | same | `connections/manage` |
| `POST /v1/instances/{id}/disconnect` | `POST /platform/connections/{connectionId}/logout` unlinks the phone. `POST .../stop` pauses without unlinking | same | `connections/manage` |

Pairing is done by a person. An agent cannot fetch or scan the QR code for the user.

### 1.3 Calls

| ZapLigue capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| `POST /v1/instances/{id}/send-call` with `phones` (up to 1,000) | `POST /messaging/voip/calls` with `connection` and `to` (E.164 or user id), once per number. Send an `Idempotency-Key`. The response carries `callId` while the callee's device rings. Placing a call also runs `POST /messaging/voip/calls/check` internally; call it first to see a refusal without placing a call | different | `calls/server` |
| `settings.waitTime` (5 to 120 s, default 30), `settings.attempts` (1 to 10, default 2), `settings.interval` (5 to 300 s, default 45) | Not offered as settings. Polymorfa has no campaign dialer, so retry and pacing logic lives in the user's code. Read each result in `call.ended` (`reason`, `direction`, `durationSeconds`) or `call.missed` and `call.rejected` | gap | `calls/how-calls-work` |
| `audioUrl` (recorded audio, MP3, OGG or M4A, played on answer) | `CallsClient` from `@polymorfa/sdk/calls` joins the call. `call.audio` carries merged signed 16-bit mono PCM at `call.audio.sampleRate`, in both directions; write audio in real time. Polymorfa does not fetch or play an audio URL for the user | different | `calls/server` |
| `uraFlowId` (visual IVR flow that listens to the caller) | Not offered as a builder. The user's code reads the call audio and runs its own speech recognition, or the user's PBX handles the menu through a SIP trunk, which carries calls in both directions | gap | `calls/sip-trunks` |
| `aiAgentId` (ElevenLabs agent, incoming and outgoing) | The user's own agent: `call.received` webhook, then `accept` (or `CallsClient` `incoming` handler), then speech services over `call.audio`. Polymorfa carries the audio and provides no recognition, synthesis or agent | different | `calls/server` |
| Live call from the panel | Browser call components (`@polymorfa/browser` with `@polymorfa/react`, or `@polymorfa/elements`) place and answer calls with client tokens | same | `calls/web` |
| One call at a time per number (each number is a channel) | A linked-device Connection holds one call at a time. `simultaneousCalls` lifts that but removes the Connection from Ban Credit; do not turn it on without telling the user | same | `calls/server#simultaneous-calls` |
| Call history with status, duration and audio, in the panel only | `GET /platform/calls`, `GET /platform/calls/{callId}` and `GET /platform/calls/export` (`format=csv` or `ndjson`, 1,000 per request). Polymorfa does not record call audio; the user's `CallsClient` code can | different | `calls/records` |
| Analytics: answer rate, hour and weekday, average duration | `GET /platform/calls/stats` with `groupBy` of `day`, `hour`, `connection` or `outcome`, `timezone`, `answerRate`, `averageDurationSeconds` and a 168-cell weekday and hour `heatmap` | same | `calls/records` |
| Share of the audio the contact listened to | Not offered | gap | none |

Call events on a webhook, none of which ZapLigue has: `call.received`, `call.accepted`, `call.rejected`, `call.missed`, `call.ended`, `call.telemetry`, `call.participant_joined`, `call.participant_state`, `call.participant_left`, `call.connection_joined`, `call.connection_left` and `call.permission_changed`.

### 1.4 Messages and broadcasts (panel only on ZapLigue)

| ZapLigue broadcast feature | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Text, image, video, audio, document | `POST /messaging/{connection}/messages/send` with `content.text`, `image`, `video`, `voice`, `file` | same | `messaging/send` |
| Interactive buttons and lists | `content.buttons`, `content.list` | same | `messaging/send` |
| `{{nome}}` variables, audiences, scheduling, pacing | Campaigns: audience members carry `variables`; launch immediately or with `scheduledAt`; `throughput.ratePerMinute`. Campaigns need a Pro Connection | more | `campaigns/send` |
| Validate which numbers have WhatsApp | `GET /messaging/{connection}/contacts/check` | same | `messaging/contacts-and-groups` |
| Delivery report | Per-recipient campaign status and `message.ack` | same | `campaigns/how-campaigns-work` |

## 2. Webhooks

ZapLigue has none. Replace the QR stream with these Polymorfa events.

| Item | Polymorfa |
| --- | --- |
| Envelope | `{"id", "connection", "timestamp", "event", "payload"}`. Dedupe on `id`; delivery is at least once and unordered |
| Signature | `X-Webhook-Signature`: lowercase hex HMAC-SHA256 over the exact raw body with the endpoint's signing secret. Verify before parsing |
| Retries | Up to 8 attempts over 24 hours. Respond with 2xx within 30 seconds after saving the event |
| Pairing events | `connection.status`, `connection.connected` (carries `phoneNumber`), `connection.logged_out` |
| Replay | `POST /platform/webhook-deliveries/{id}/retry`, `POST /platform/events/{eventId}/replays` |

See `development/webhooks` and `api-events`.

## 3. Behaviour differences a migrating agent must handle

1. **No campaign dialer and no IVR builder.** A `send-call` campaign has no one-call equivalent. List every `send-call` in the code, show the user the audio, flow and agent ids it uses, and agree for each campaign: code that places calls at a pace the user approves, or leave the campaign on ZapLigue. Never loop over a large list without approval.
2. **Calls at volume.** Polymorfa advises against unsolicited or high-volume calls from a linked-device Connection and recommends a Cloud API Connection for business-initiated calls at volume, where the person has granted permission. Cloud API calls are one-to-one audio. Tell the user before moving cold-list calling. See `calls/best-practices` and `calls/permissions`.
3. **Check before calling.** `POST /messaging/voip/calls/check` returns `allowed` and a `refusal` of `calls_disabled`, `call_recipient_opted_out`, `call_destination_blocked`, `call_permission_required` or `call_limit_reached`. Respect the team do-not-call list.
4. **Call allowance.** Each Connection tier includes outbound calls per month: Free 5, Standard 50, Pro unlimited. A Standard Connection pays 20 credits for each call beyond 50. See `billing/connection-tiers`.
5. **Disconnected Connections.** ZapLigue answers `422` when an instance is disconnected. Polymorfa refuses a send to a disconnected Connection with `503 connection_not_ready`, so read the Connection's `status` before placing calls, hold work in the user's own queue and retry with the same `Idempotency-Key`.
6. **Billing model.** ZapLigue charges R$ 49,90 per connected number a month (R$ 44,91 above 5 numbers). Polymorfa charges per online Connection-day by tier, so a disconnected day costs nothing. See `billing/connection-tiers`.
7. **Test connections.** Test Connections run on a simulated network at 0 credits and follow the tier's call allowance: 5 inbound and 5 outbound calls a month on Free. Do not load-test calling there. See `testing/test-connections`.
8. **Async completion.** Restart and logout return `202` plus an operation id. Wait for `connection.status` before the next step.
