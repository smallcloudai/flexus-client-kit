---
name: welcome-email-setup
description: Guide the user through setting up a welcome email template and automation for new contacts.
---

# Welcome Email Setup

1. Check company info and products silently (/company/summary, com_product)
2. If missing critical data (company name, value proposition), ask user to provide it first
3. Draft a welcome email template using available data — show it to the user
4. Ask if they want to adjust the tone, add specific info (links, offers, next steps), or use their own template entirely
5. Iterate until they're happy with it
6. Store template in /sales-pipeline/welcome-email
7. Create automation with crm_automation tool
