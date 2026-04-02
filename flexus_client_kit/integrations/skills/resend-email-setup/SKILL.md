---
name: resend-email-setup
description: Guide the user through setting up email sending domains, configuring EMAIL_RESPOND_TO, and understanding email capabilities.
---

# Email Setup

## Domain Setup

Use `email_setup_domain(op="help")` to see all available operations.

Strongly recommend a subdomain (e.g. mail.example.com) instead of the main domain, especially for inbound emails.

Steps:
1. Ask the user for their domain and whether they want to receive emails on it
2. Call `email_setup_domain(op="add", args={"domain": "...", "region": "...", "enable_receiving": true/false})`
3. Show the DNS records to the user — they need to add these in their DNS provider
4. After they confirm DNS is set, call `email_setup_domain(op="verify", args={"domain_id": "..."})`
5. If verification fails, check status and help them fix DNS records

If no domain is configured yet, the user can send from the testing domain — call `email_setup_domain(op="help")` to see it.

Never use flexus_my_setup() for email domains — they are saved automatically via the email_setup_domain() tool.

If the user wants to use their own Resend account, they should connect it via the Integrations page — the webhook is created automatically on connect.

## EMAIL_RESPOND_TO

Users can configure EMAIL_RESPOND_TO addresses in bot setup. Emails to those addresses become tasks the bot handles. All other inbound emails are logged as CRM activities only.

## What You Can Send

Allowed: transactional, replies, welcome emails, follow-ups to contacts who had a conversation or requested info.
Forbidden: cold outreach, mass campaigns to contacts who never interacted, bulk promo without opt-in.
