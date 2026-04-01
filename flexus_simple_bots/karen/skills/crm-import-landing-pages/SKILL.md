---
name: crm-import-landing-pages
description: Guide the user through setting up a contact import form on their landing page or website — HTML form template, API endpoint, required and optional fields.
---

# Importing Contacts from Landing Pages

When users ask about importing contacts from landing pages or website forms, explain they need their form to POST to:

https://flexus.team/v1/erp-ingest/crm-contact/{ws_id}

Required fields:
- contact_email
- contact_first_name
- contact_last_name

Optional fields: Any contact_* fields from the crm_contact table schema (use erp_table_meta() to see all available fields), plus any custom fields which are automatically stored in contact_details.

Provide this HTML form example and tell users to add it to their landing page using their preferred AI tool, or customize and add it themselves:

```html
<form action="https://flexus.team/v1/erp-ingest/crm-contact/YOUR_WORKSPACE_ID" method="POST">
  <input type="text" name="contact_first_name" placeholder="First Name" required>
  <input type="text" name="contact_last_name" placeholder="Last Name" required>
  <input type="email" name="contact_email" placeholder="Email" required>
  <input type="tel" name="contact_phone" placeholder="Phone">
  <textarea name="contact_notes" placeholder="Message"></textarea>
  <button type="submit">Submit</button>
</form>
```
