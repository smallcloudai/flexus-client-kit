---
name: collect-support-knowledge-base
description: Use this skill to setup your knowledge base, improve your setup, edit /support/summary, change tone of voice, setup daily reporting, setup human escalation.
---


# To Work Efficiently You Need to Know Stuff

Your only job is to take care of /support/summary policy document, create it or improve it. It will
take several steps, call `support_collection_status` after each step to minimize mistakes.

You did something with draft => call support_collection_status.

Changing other policy documents is not your job, don't touch them.


## Sources of Information

Here is what you can use:

- Business homepage
- Documentation website
- Any documents they can upload (user clicks "Upload Documents" in group, dnd files, they appear as an EDS)
- Google Drive (EDS)
- Dropbox (EDS)
- Model Context Protocol (MCP)

Set up EDS here in this chat. A simple homepage with pictures and animations is not suitable for EDS usually,
but if it has FAQ and return policy sections, that's very helpful, create a crawler EDS, later
flexus_vector_search() will be able to pages like "return policy" and answer questions, exactly what we need.

If you have a documentation website, that's perfect. Make EDS using flexus_eds_setup() for documentation to be
indexed and then accessible using flexus_vector_search().

Set up MCP here in this chat. The newly created MCP tool will only be available after chat restart,
so you will not be able to test MCP yourself, but you can send a explore_a_question() subchat to check it.

Don't call flexus_vector_search() yourself. The output of vector search is typically long, and you run the risk
of overflowing the context and failing your mission. Use explore_a_question() instead: explore website, documentation,
the newly created EDS, MCP.

First call must be always to test if the source is working, call only 1 in parallel.
Chances are high it will not work at all, and it will need troubleshooting.

Once you see evidence that it works, then you can call up to 5 in parallel, or give it up to 5 sources to
run in parallel, no problem.


## Files Attached to Chat

If the user attaches a file to this chat, warn them that the file should be uploaded to your group,
to be accessible to the next chat. Make it a big **WARNING** because it's a common mistake. An attached file
is great for summarizing it into a policy document, but it will not be present in future chats with clients.


## You Have Nothing

If your file /support/summary does not exist, you need to ask the user for any information they have.

Have a session of extracting documents and information from the user, go nuts.

After that done, run explore_a_question("summarize the nature of business") or any question you need.
If that does not work or the user does not have any documentation at all, then ask user.

Once you have reasonably good idea of what the nature of business is, create a draft like this:

```
flexus_policy_document(op="create_draft_qa", args={
      "output_dir": "/support/",
      "slug": "summary-v1",
      "top_tag": "support-policy",
      "sections": {
          "product": ["description", "icp", "links", ...],
          "payments": ["normal-work", "refunds", "discounts", ...],
          "sources": ["working-eds", "working-mcp", "working-websites"],
          "answering": ["tone-of-voice", "offtopic"],
          "restrictions": ["never-say", "forbidden-promises", "legal-disclaimers"],
          "reporting": ["daily", "weekly"],
          ...
      }
  })
```

This will write /support/YYYYMMDD-DRAFT-summary-v1 policy document with QA structure inside.

After creating the draft:

1. Call `translate_qa` to set human-readable question text in the user's language
2. Pre-fill any answers you can derive from what you have gathered so far
3. Call `support_collection_status` to confirm progress
4. Then continue filling fields as you research user's documents

The structure of the summary is not fixed. Look at inspiration lists below and come up with sections and questions
tailored for the situation at hand. It should be several sections, multiple questions in each, the structure is
not changeable later, you have to create a new draft, so do your best. Make sure you have "answering", "restrictions",
and "reporting" sections in any case.

ALWAYS ask the user what support should NEVER say. This goes into the "restrictions" section: forbidden promises,
competitor comparisons they don't want made, legal/medical/financial disclaimers, roadmap dates, internal pricing
details, etc. The customer-facing expert enforces these hard -- missing restrictions means the bot will improvise.

The user can participate in filling the document, should be no problem working on it together with the user at the
same time, once the structure is in place.


## You Have Something, but User Wants Improvements

Small change => you can write an update to `/support/summary` using op=update_at_location.

Big change => create a new draft with slug="summary-v{N+1}", improving the structure. Then fill in the fields one by one as you research
user's documents.


## Moving Draft to Summary

You did something with draft => call support_collection_status.

Ask user to review the policy document. After they confirm that's what they want, use op=mv with /support/summary as
the destination.

You think you've finished => call support_collection_status to confirm.


## Inspiration

Some lists of things to know for different use cases.


### SaaS

What does the product actually do? One paragraph, plain language — the agent's identity anchor for every reply.
What are the pricing tiers and what's included in each? Agents get this question constantly and a wrong answer creates churn.
What is the trial/onboarding flow? How does a new user go from signup to first value? Where do they get stuck?
How does account/user management work? Adding seats, changing roles, transferring ownership, deleting accounts.
What integrations exist, and what are their known limitations? "Does it work with X?" is a top pre-sales and post-sales question.
What is the cancellation and refund policy, verbatim? Agents quote this; paraphrasing creates liability.
Where is the status page, and what's the incident communication protocol? Outages trigger a ticket flood — the agent needs a canned response and a live URL.
What's the data/privacy policy in plain language? Enterprise and regulated-industry customers ask this often; a wrong answer can kill a deal.
What situations require escalation to a human or specialist? Billing disputes, data loss, legal/compliance questions, enterprise SLA breaches.
What should the agent never say? Competitors not to mention, roadmap claims not to make, promises about uptime/data recovery they can't keep.


### Internet Shop with Physical Delivery

What are the shipping methods, costs, and estimated transit times — by region? Order tracking and shipping status is the single most frequent question, accounting for roughly 30% of all tickets. Ringly
What is the return/exchange policy, verbatim? Window, conditions, who pays return shipping, whether in-store return is possible.
What is the refund process? How long, to which payment method, store credit vs. original method.
How do customers track their order? Where the tracking link is sent, what to do if it's missing or stale.
What happens when an order arrives damaged, wrong, or missing items? The exact resolution path: replacement, refund, photo requirements.
Can orders be modified or cancelled after placement? Time window, how to do it, what happens if it's already shipped.
What payment methods are accepted, and why do payments fail? Including buy-now-pay-later, gift cards, and declined card troubleshooting.
What is the product — materials, sizing, compatibility, care instructions? Agents need a searchable product knowledge base; "is this right for me?" questions are high-volume pre-purchase.
Are there discount codes, loyalty programs, or promotions active right now? Customers ask why a code isn't working or whether a sale applies to their order.
What situations require escalation? Fraud suspicion, lost parcels in transit beyond X days, legal complaints, chargeback disputes.


### Healthcare / Clinic

What services are offered, and which conditions/cases fall outside scope? Agents must know what they can and can't direct patients toward.
How does appointment booking, rescheduling, and cancellation work? Including lead times, cancellation fees, and waitlist procedures.
What insurance plans are accepted, and what does coverage typically include? Privacy compliance and understanding insurance policies are core competencies agents need before handling any patient inquiry. Help Scout
What are the out-of-pocket costs and payment options? Self-pay rates, payment plans, what triggers a bill.
What is the patient data and privacy policy (HIPAA/local equivalent)? Agents must know what information they can and cannot share, and with whom.
How do patients access test results, prescriptions, or referrals? Portal login, turnaround times, who to call if something is missing.
What is the after-hours and emergency protocol? Who to call, what the agent should say, when to direct to emergency services.
What are the preparation instructions for common procedures? Fasting requirements, medication holds, what to bring.
What is the complaint and feedback escalation process? Who handles a patient who is distressed, dissatisfied, or making a formal complaint.
What must the agent never do? Provide clinical advice, interpret results, make diagnostic statements — hard lines with legal and regulatory consequences.


### Restaurant / Food Service (Booking + Delivery)

What is the menu, including allergens, ingredients, and dietary options? "Is this gluten-free / nut-free / vegan?" is the highest-frequency food question.
How does reservation/booking work? Platform used, cancellation window, deposit policy, group/private dining rules.
What is the delivery area, delivery time estimate, and minimum order? Including third-party platform policies vs. direct delivery differences.
What is the refund/remake policy for wrong or unsatisfactory orders? Photo required? Replacement vs. credit vs. refund?
What promotions, vouchers, or loyalty rewards are currently valid? And what's excluded (e.g., doesn't apply to delivery or alcohol).
What are the opening hours and holiday schedule? Including any seasonal changes.
How are special dietary/allergy requests handled in the kitchen? The agent needs to know the honest answer — cross-contamination risks especially.
How does the ordering/payment platform work? Common checkout issues, missing confirmation emails, failed payments.
What are the catering and large-group ordering options? Lead time, minimums, deposit.
What situations must go to a manager? Food safety complaints, alleged allergic reactions, media/PR inquiries, aggressive customers.
