---
name: update-company-summary
description: Create or update the /company/summary policy document by gathering company info from user conversation or their website
---

How to create or update `/company/summary` — the heavily summarized document that other bots (sales, marketing, support) read to understand the company.

Check if it already exists or not. If not, create it from template first:

flexus_policy_document_from_template(output_dir="/company", slug="new-summary-draft", template="company-summary")

Then start filling it with useful information. Ask the user for website, or a pdf, or just ask questions.
If it's a website, use both the text version and a screenshot of the first page.

Fill the fields that you can, ask the user if they want to change anything, if it's all fine then run:

flexus_policy_document(op="mv", args={"p1": "/company/YYYYMMDD-new-summary-draft", "p2": "/company/summary"})
