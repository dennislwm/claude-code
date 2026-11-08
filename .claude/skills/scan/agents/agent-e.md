# Agent E: PSA trends (the last three cells of section 4)

Read common.md and gemrate.md first. **Route:** on the card page run a script that clicks the link whose text is `PSA set details` (it opens in the same tab). **Fallback:** click it by coordinates.

Its "Recent Trends" table has one row per card. Read it with get_page_text straight after the page loads, before any scrolling: after a sideways scroll the Recent Trends columns were missing from the page text. If the columns are missing, scroll the table and confirm the card's row with one zoomed screenshot. Find the card's row by name and number (a promo set may have many rows) and read graded past month and graded prior month.

Return only:

```
PAST MONTH: <n>
MONTH BEFORE: <n>
```
(or `not read: <reason>` for either line)
