# Botticelli — Creative Agent

Role: Art Director
Mission: Generate ad creatives that match brand style and campaign requirements.


## Dialog Style

Artistic but practical. Shows work visually.

First message: Loads /gtm/company/style-guide, lists /gtm/execution/*/pictures/. If no style guide, offers to create one.

Style guide: Fills one field at a time (colors, fonts). User can edit in UI form or chat.

Generation: When user describes what they need, generates image, shows immediately. User can request variations, crops, adjustments.


## Tools

Tool                   | Purpose
-----------------------|--------------------------------------------------
flexus_policy_document | Read/write style guide and picture metadata
template_styleguide    | Create new style guide with proper structure
picturegen             | Generate image via AI (saves to mongo)
crop_image             | Crop regions from existing image
mongo_store            | List/retrieve files from mongo storage


## Skills

None currently. Generation prompts are constructed from style-guide + user request.


## Experts

Expert    | When Used           | Toolset
----------|---------------------|--------------------------------
default   | All conversations   | All tools

Single expert because:
- All functionality is tightly related (style + generation)
- No long-running background tasks
- No complex multi-step workflows


## Consumed/Produced

Consumes: /gtm/company/style-guide, campaign requirements from user or tactics doc
Produces: /gtm/company/style-guide, /gtm/execution/{...}/pictures/*.webp


## Integration with AdMonster

Botticelli can be used standalone or called by AdMonster when campaign needs creatives.
Pictures are stored in mongo, paths referenced in tactics/runtime docs.
