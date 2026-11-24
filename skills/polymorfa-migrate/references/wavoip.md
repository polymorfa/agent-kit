# Wavoip reference for polymorfa-migrate

Maps Wavoip (https://wavoip.com, docs at https://wavoip.gitbook.io/api) to Polymorfa. Checked on 24 November 2026 against Wavoip's published documentation and Polymorfa's documentation. Confirm each Polymorfa operation in the current docs (https://docs.polymorfa.com/llms.txt) before you change code; docs pages are given as content paths, for example `calls/server` is https://docs.polymorfa.com/calls/server.

Status: `same` (direct equivalent), `more` (equivalent with more), `different` (covered another way; read the note), `gap` (not offered; agree a replacement with the user).

The human guide is https://docs.polymorfa.com/migrate/wavoip.

Wavoip carries WhatsApp calls only. It documents no message sending. If the project also sends messages through another stack on the same number, ask the user whether to move them to the same Polymorfa Connection.

## Requests and credentials

Wavoip: a JWT from `POST /v2/auth/login` (email and password) authorizes the REST API under `/v2`. The JavaScript library takes device tokens: `new Wavoip({ tokens: [...] })`. A device token is a UUID shown on the device page. A sign-up token does not expire and there is no refresh flow. The REST docs list no API key.

Polymorfa: `Authorization: Bearer <project token or team key>` with scopes such as `connections:manage`. Browsers use a short-lived client token bound to one Connection, with the `voip_place`, `voip_answer` and `voip_signal` actions allowed in the Connection's client rules. Client tokens act as `client:<ephemeralId>`, server credentials as `server:<participant>`. Native paths start with `https://api.polymorfa.com/messaging/{connection}` or `https://api.polymorfa.com/platform`.

## Mapping

| Wavoip capability | Polymorfa equivalent | Status | Docs page |
| --- | --- | --- | --- |
| Device linked by scanning a QR code | QuickLink, by QR code or pairing code, on a hosted page with the user's brand; or direct pairing | more | `connections/quicklink`, `connections/direct-pairing` |
| Linking by OTP code | Pairing code (Wavoip says its OTP route is not yet available) | more | `connections/quicklink` |
| Official number linked with a WABA login or Embedded Signup (`waba-link`, `waba-signup`) | QuickLink that offers Meta Cloud API, through Embedded Signup. Beta, needs team access | same | `connections/cloud-api-setup` |
| External session bridged from Baileys or Evolution | Import the Baileys session. Never run the source and the imported copy at the same time | different | `connections/import-connections` |
| Device status, `restart`, `logout` | `GET /platform/connections/{connectionId}`, `POST .../restart`, `POST .../logout`, each with an event | same | `connections/manage` |
| Reseller clients (`clientId`) | Customers: customer records, pairing links and a monthly cap per customer | different | `customers` |
| Reseller price table and wallet | Not offered | gap | none |
| `startCall({ to })` in `@wavoip/wavoip-api` | `POST /messaging/voip/calls` or `messaging.voip.place`; `Idempotency-Key` supported | more | `calls/server` |
| `offer` event and `offer.accept()` | `call.received` event and `POST /messaging/voip/calls/{id}/accept` | same | `calls/server`, `calls/how-calls-work` |
| `peerAccept` and `ended` call events | `call.accepted` and `call.ended` | same | `calls/how-calls-work` |
| Webphone and Click To Call widget | `@polymorfa/browser` with the call components (`@polymorfa/react` or `@polymorfa/elements`) | same | `calls/web` |
| SIP trunk to a PBX (device token or account login as credentials) | SIP trunks: `GET /platform/sip/endpoint`, `POST /platform/sip-trunks`. Inbound credentials are shown once. Audio only | same | `calls/sip-trunks` |
| Channels: one concurrent call each | `simultaneousCalls` call setting on a linked-device Connection. Read its risk notes in the docs before turning it on | different | `calls/server` |
| Device behavior `incoming_calls`, `reject_calls`, `allow_unknown_calls` | Per-Connection call settings (`callsEnabled`), `POST /messaging/voip/calls/{id}/reject`, a team do-not-call list and blocked country codes | different | `calls/server`, `calls/permissions` |
| `GET /v2/calls`, `/v2/calls/analytics`, `/v2/calls/export` | Call history and summary in the Console, `GET /platform/calls`, and `GET /platform/calls/export` (CSV or NDJSON) | same | `calls/records`, `calls/console` |
| `GET /v2/calls/{id}/statistics` | `call.telemetry` event and call records with timing and quality figures | same | `calls/records` |
| Call flow as SIP and Meta PCAP | Not offered | gap | none |
| Call recording (`record_calls`, `record.updated`, recording URLs) | Not offered. Polymorfa does not record call audio or video | gap | `calls/records` |
| Call campaigns that dial a list and play a recorded audio (`/v2/campaigns`) | Not offered. Polymorfa cannot play an audio file on a call yet; use your own server code with `CallsClient` to speak and listen | gap | `calls/server` |
| Server-sent event streams for the dashboard (`/v2/devices/events`) | Webhooks for server code. Event streams are a beta that needs team access | different | `development/webhooks`, `development/event-streams` |
| Device and subscription purchase (`/v2/sales`) | Not offered. Each Connection is billed for its online days from credits | gap | `billing/usage` |
| Hosted MCP server | Hosted MCP server with 150+ tools, and a local MCP in the CLI | more | `development/mcp` |

## Webhooks

Wavoip: one webhook per device, configured with `PUT /v2/devices/{deviceId}/webhook/settings` (`url`, `active`, `call_event`, `record_event`, `device_event`). The body is JSON with `event`, `id_session`, `type` (`CALL`, `RECORD`, `DEVICE`) and `action`. The header `X-Wavoip-Delivery-Id` is stable per delivery. A non-2xx answer or a 15-second timeout is a failure; retries follow after 5 seconds, 30 seconds and 5 minutes, then the device's webhook is switched off until re-enabled. Delivery is at least once. No signature is documented.

Polymorfa: events go to one signed endpoint. `X-Webhook-Signature` is HMAC-SHA256 over the raw body in lowercase hex, with no timestamp in the signed string. A failed delivery is retried up to 8 times over 24 hours, never switched off, and the delivery log supports replay. `X-Polymorfa-Delivery-ID` is the same on every attempt of one delivery. See `development/webhooks`.

| Wavoip event | Polymorfa | Status |
| --- | --- | --- |
| `call.created` | `call.received` for an inbound call; the `callId` in the place response for an outbound one | same |
| `call.updated` | `call.accepted`, `call.rejected`, `call.missed`, `call.ended` | same |
| `record.updated` | Not offered | gap |
| `device.opened`, `closed`, `connecting`, `hibernated`, `building`, `restarting`, `error` | `connection.status` | same |
| `device.logged-out` | `connection.logged_out` | same |
| `device.phone_updated` | Not offered | gap |
| `device.timelock_updated` | `connection.restriction_updated` | same |
| `device.waiting_payment`, `device.overdue` | Not offered. Polymorfa bills each Connection for its online days from credits | gap |

`call.ended` carries `reason`, `direction` and `durationSeconds`; `call.telemetry` follows. The published catalog also has `call.participant_*`, `call.connection_*` and `call.permission_changed` events. Check each event in the Polymorfa webhook docs before you rely on it.

## Calls on Polymorfa

Calls run in a browser, from server code and over SIP, in both directions. Linked-device Connections take voice, video and group calls. Cloud API calls are one-to-one audio, and the recipient must grant call permission first. Polymorfa refuses a call or invite with `403 connection_restricted` while WhatsApp restricts the Connection to people it has chatted with. `POST /messaging/voip/calls/check` runs the placement checks without calling. Outbound starts are limited to 30 a minute per source Connection.

## Differences to agree with the user

- Polymorfa does not record calls and cannot play audio on a call yet. Find code that reads recordings, `record_calls`, `record.updated`, recording URLs or `/v2/campaigns`, and agree a replacement.
- Wavoip sells devices with channels and bills new subscriptions monthly. Polymorfa bills each Connection per online day from credits, and a Standard Connection includes unlimited inbound calls and 50 outbound calls a month. Remove purchase and channel-resize code.
- Replace the unsigned Wavoip webhook with a raw-body signature check, and deduplicate on `X-Polymorfa-Delivery-ID` instead of `X-Wavoip-Delivery-Id`.
- Wavoip device ids (integers), device tokens, call ids, `whatsapp_call_id` values and client ids do not carry over. Polymorfa ids are opaque strings; look them up again. Export call history from Wavoip first if the user needs it.
- Calls to people who never chatted with the Connection are the riskiest behavior on both platforms; keep the user's warm-up and permission rules.

## Move in this order

1. Add the Polymorfa credential and webhook secret to the secret store.
2. Add the Polymorfa webhook route next to the Wavoip one and verify signatures.
3. Put call code behind one adapter, so each number switches by configuration.
4. Pair the first number through QuickLink and place a test call.
5. Switch that number's traffic, watch `call.accepted` and `call.ended`, then move the next number.
6. Repoint each PBX to its Polymorfa trunk. Cancel the Wavoip device only after the number runs on Polymorfa.
