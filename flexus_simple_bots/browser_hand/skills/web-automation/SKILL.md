---
name: web-automation
description: Web automation reference for CSS selectors, common workflows, and error recovery
---

## CSS Selector Reference

### Basic Selectors
- `#id` — Element by ID
- `.class` — Elements by class
- `tag` — Elements by tag name
- `tag.class` — Tag with specific class

### Form Selectors
- `input[type="text"]` — Text inputs
- `input[type="email"]` — Email inputs
- `select` — Dropdown menus
- `textarea` — Text areas
- `button[type="submit"]` — Submit buttons
- `input[name="fieldname"]` — Input by name attribute

### Navigation Selectors
- `nav a` — Navigation links
- `a[href*="login"]` — Login links
- `.breadcrumb` — Breadcrumb navigation
- `.pagination` — Pagination controls

### Content Selectors
- `main` — Main content area
- `article` — Article content
- `.product-card` — Product listings
- `.price, [data-price]` — Price elements
- `table` — Data tables
- `h1, h2, h3` — Headings

## Common Workflow Templates

### Price Comparison
1. Search for product on each site
2. Extract price, availability, shipping cost
3. Normalize currency and format
4. Generate comparison table

### Content Extraction
1. Navigate to target page
2. Identify content structure (selectors)
3. Extract text, images, links
4. Format as structured data

### Form Submission Guide
1. Navigate to form page
2. Identify all required fields
3. Present field list to user for values
4. Describe how to fill each field

## Error Recovery

### Element Not Found
- Try alternative selectors
- Check if content is dynamically loaded
- Try full-page screenshot to see current state

### Timeout
- Retry with longer timeout
- Check if site is accessible
- Try alternative URL or cached version

### CAPTCHA Detected
- Do NOT attempt to solve
- Inform user that manual intervention is needed
- Suggest alternative approaches

### Pop-ups/Modals
- Look for close buttons: `.close`, `[aria-label="Close"]`, `.dismiss`
- Try pressing Escape key
- Check if content is accessible behind modal

## Security Checklist
- Verify domain matches expected (no typosquatting)
- Check for HTTPS (padlock icon)
- Never enter credentials unless user explicitly provides them
- Watch for phishing indicators (misspelled domains, suspicious redirects)
- Report any security concerns immediately
