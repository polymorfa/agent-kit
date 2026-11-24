---
name: polymorfa-migrate
description: Move an existing WhatsApp integration from another provider (such as Z-API) to Polymorfa, mapping every API call, webhook and connection without losing any.
---

# Move a WhatsApp integration to Polymorfa

Use this skill when a project already sends or receives WhatsApp messages through another provider and the user wants some or all of it on Polymorfa. Read the provider's reference in `references/` before planning. References, one per provider: `references/z-api.md` (Z-API), `references/1msg.md` (1MSG), `references/green-api.md` (Green API), `references/timelinesai.md` (TimelinesAI), `references/botconversa.md` (BotConversa), `references/whaticket.md` (Whaticket), `references/zapligue.md` (ZapLigue), `references/360dialog.md` (360dialog), `references/twilio.md` (Twilio), `references/vonage.md` (Vonage), `references/gupshup.md` (Gupshup), `references/infobip.md` (Infobip), `references/bird.md` (Bird). If the provider has no reference, follow the matching migration guide under https://docs.polymorfa.com/migrate/, the [agent index](https://docs.polymorfa.com/llms.txt) and the provider's own documentation, and say that no reference exists.

## 1. Inventory before you change anything

Search the whole project, including tests, scripts, infrastructure and environment files, and list every place that uses the provider:

- outgoing requests (each endpoint and message type)
- webhook routes and the event types they handle
- stored provider identifiers: instance or channel ids, message ids, group ids, media URLs
- credentials and environment variables
- scheduled jobs, queues and retries that wrap provider calls
- connected numbers and who owns them

This inventory is the checklist for the whole move. Report the count of each kind and anything you cannot map. Never print credentials or phone numbers in the report.

## 2. Agree the scope

Tell the user what you found and ask what to move now: one feature, one number, a customer, or everything. Do not assume a full migration. Ask before pairing a production number, sending a message, creating or deleting remote resources, or incurring charges.

## 3. Map each item

Use the provider reference to map each inventory line to a Polymorfa operation, event or setting. Confirm each mapping against the current Polymorfa documentation through the documentation MCP or the [agent index](https://docs.polymorfa.com/llms.txt). Do not invent endpoints, fields, event names or SDK methods. When the reference marks a row as a gap or a behaviour difference, tell the user and agree how to handle it.

## 4. Move in a reversible order

1. Add Polymorfa credentials through the project's secret mechanism.
2. Add the Polymorfa webhook route next to the old one. Verify signatures on the raw request body; use the polymorfa-webhooks skill.
3. Put sending behind one adapter so each caller switches by configuration, not by editing every call site.
4. Pair connections through QuickLink only when the user approves, number by number.
5. Switch traffic per number or per customer, keep the old provider working, and confirm with the user before anything on the old provider is disconnected, deleted or cancelled.

## 5. Verify and report

Use permitted reads first. Exercise sends, webhooks and failure paths only with the user's approval. Finish with the inventory: each item, its Polymorfa replacement, and whether it was moved, verified, or left for later, with the reason.
