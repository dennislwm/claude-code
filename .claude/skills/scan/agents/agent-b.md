# Agent B: PSA row (the first three cells of section 4)

Read common.md and gemrate.md first. On the card page, read the PSA row with `get_page_text`: population, gems and gem rate, as the page shows them. If the page still says "Card not found" after the retry in gemrate.md, print `not read: card page not found` for each line, and add the search tile's totals only if you label them "all graders, not PSA".

Return only:

```
POPULATION: <n>
GEMS: <n>
GEM RATE: <one decimal>%
```
(or `not read: <reason>` for any line)
