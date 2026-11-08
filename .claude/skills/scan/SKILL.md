---
name: scan
description: Look up one Pokemon card or sealed product from a short description (for example "mew 051 jap from cp6") or a photo of the card on SnkrDunk, Collectr, GemRate and CardLadder, and reply in one fixed template. Read-only. Use when the user types /scan, sends a photo of a card, or asks for a card show price check.
---

# scan

## Rules

- Read only. Never sign in, buy, bid, message or change anything on any site. Stop at a bot challenge or sign-in page and print `not read: <reason>` for that source.
- Never guess. A figure that was not read prints `not read: <reason>` in its own cell.
- When several candidates agree, ask the jev skill to pick. Accept a pick strictly above 0.6. Otherwise the match is `not matched`.
- Browser steps use the claude-in-chrome skill. Chain navigate, a 3 second wait, then find or get_page_text in one browser_batch call. Pages load late: wait until the price or population appears. Use only the tab id you were given. Never close a tab and never call tabs_context_mcp or tabs_create_mcp: in one run, agents closing and creating tabs at the same time removed each other's tab group.

## Steps

1. **Parse the input** into name, number, set code and language. The input is a typed description, or an image of a card or a graded slab. "jap", "jp" or "japanese" in text means Japanese, and so does a card whose text is Japanese. Anything else means English.
   - From an image, read the name, the number as printed (for example `051/087`), the set code only if it is printed as text (a set symbol is not a code), the language from the card text, and from a slab label also the grade and grader.
   - If the name or the number cannot be read with certainty, the match is `not matched`. Never identify a card from its art alone.
   - If there is no text and no image, print exactly `Send a card description (for example "mew 051 jap from cp6") or a photo of the card.` and stop.
2. **Rate.** `curl -sL "https://api.frankfurter.dev/v1/latest?base=SGD&symbols=JPY,USD"` gives units per SGD, so SGD = amount / that currency's rate. If that fails, try `https://open.er-api.com/v6/latest/SGD`. If both fail, print the original price and `SGD: not read`. Never show the rate.
3. **Get one tab per agent first:** four for an English card (agents A, B, C and E), five for a Japanese card (it adds agent D). Call tabs_context_mcp with createIfEmpty. If the group already has enough tabs from an earlier scan, use the first ones as they are. Otherwise call tabs_create_mcp until there are enough. No agent creates or closes a tab. **Then start every agent in one message** (general-purpose agents, so they run in parallel). Each works alone and never waits for, or reads from, another agent. Each agent's steps live in a file in this skill's `agents/` folder (roster below). Give each agent only: the full path of its file and of `agents/common.md` (and `agents/gemrate.md` for B, C and E), the card fields (name, number, set code if legible, language), a search query, the rates, and its own tab id. It reads its files itself, in one step. Each returns only what its file says, or `not read: <reason>`; a failed agent prints `not read: agent failed`. Do no other browser work yourself. Print the header line, then each section with its numbered heading as soon as it is ready, in whatever order. Finish every tool call for that turn first, then print, and end the turn right after printing (no tool call after printed text). When the last agent has returned, run all the remaining tool calls (derive, awk, the Summary checks) first, then print every section and the Summary in one message. Section 4 is ready when both B and E have returned; compute its Change cell with awk. Agent D prints no section. For a Japanese card, build section 3 as soon as A returns: run `derive.sh` for the SnkrDunk yen median, range and PSA 10 ask-vs-median lines, compute sales per day (the PSA 10 count over its days) with awk, take the window from A's `WINDOW PSA10` line, and print sections 1 and 3 together. When all agents are done, leave the tabs open for the next scan (closing tabs removed the tab group in earlier runs), draft the Summary, check each sentence as the Summary rules say, then print it last.

### Agents

| Agent | File in `agents/` | Reads | Returns |
|---|---|---|---|
| A | `agent-a.md` | SnkrDunk for a Japanese card, Collectr for an English card | section 1 (and section 3 for an English card), a `SET` line, `DATA` lines and a `WINDOW PSA10` line; for a Japanese card the main session builds section 3 |
| B | `agent-b.md` | the GemRate PSA row | population, gems, gem rate (section 4, first three cells) |
| C | `agent-c.md` | CardLadder, reached from the GemRate card page | section 2 |
| D | `agent-d.md` | Collectr, Japanese cards only | Collectr prices for the Summary, no section |
| E | `agent-e.md` | the GemRate PSA set details table | graded past month and month before (section 4, last three cells) |

The Template below is the authority. An agent file repeats the format of its own section, so change the two together.

## Shot mode

`/scan shot <description or image>`: the first word `shot` selects it. Same parse (step 1) and `not matched` rule; the reply is screenshots only, with no template, no Summary and no `why` checks. Skip the rate (step 2), agents D and E and `derive.sh`. E is out: its set details page returned no results in the one run, so the GemRate trend cells are not shown.

- Get three tabs (step 3) and start agents A, B and C in parallel. Add this line to each prompt: "SHOT MODE. Do your route as written up to the final page, do not read or return figures, take no screenshot for output, leave the tab on that page, reply with exactly `DONE` or `not read: <reason>`." For C, the final page is the CardLadder sales list. For B, it is the GemRate card page scrolled to the Population by Grader table, whose PSA row holds the population, gems and gem rate. For A, it is the SnkrDunk apparel page (Japanese) or the Collectr card page (English).
- As each agent returns, take the screenshot yourself with the `computer` tool on that tab (scale 0.6; 0.8 for GemRate). For an English card, also take one `zoom` (region `[480,0,980,480]`) of the Collectr graded legend, which holds the graded prices. Scroll first with `javascript_tool`, not the scroll action, which adds an unwanted image: `const c=[...document.querySelectorAll('*')].filter(x=>x.textContent.trim()=='Graded Price History');c[c.length-1].scrollIntoView({block:'start'});window.scrollBy(0,-20)`. For a Japanese card, also take one screenshot of the SnkrDunk sold history on the same page, scrolled the same way: `const e=[...document.querySelectorAll('*')].find(x=>x.children.length==0&&x.textContent.trim()=='売買履歴');e.scrollIntoView({block:'start'});window.scrollBy(0,-140)`. It shows recent sales with mixed grades, not the full list; click no chip. Never scroll GemRate yourself: that domain denied it. Agent screenshots do not reach the user; only the main session's do. Never set `save_to_disk` and never call SendUserFile: the inline image is the delivery, and nothing is persisted.
- Print one line before each shot naming the page, or `not read: <reason>` where an agent failed. Add no other commentary: no description of what a page shows, no summary, no follow-up offers.

## Template

Fixed order, fixed columns, fixed labels. Never add, drop or rename a column or section. At most 5 rows per table; extra rows go in one `Also listed:` line in the same order. Yen has thousands separators and no decimals. SGD has two decimals. Percentages have one decimal and a sign. Rows run from lowest to highest grade (raw first, then PSA, BGS, CGC), then newest first.

    ## <name> <number>/<size>, <set> (<language>)

    ### 1. Prices
    Japanese:
    | Grade | Ask (JPY) | Ask (SGD) | Last sold (JPY) | Ask vs last sold |
    No listing: <grades with no ask>.
    English:
    | Grade | Price (SGD) |
    (a `Graded | not read: none listed` row when no graded price is shown)

    ### 2. Last sold (CardLadder)
    | Grade | Date | Type | Price (USD) | Price (SGD) |
    Marketplace: <name shown on the listings; if they differ, name each after its grade>.

    ### 3. Trend
    Japanese (SnkrDunk), rows: Median sold PSA 10 (JPY), Range sold PSA 10 (JPY), Median sold raw (JPY), Range sold raw (JPY), Ask vs median (PSA 10), Sales per day (PSA 10), Window (PSA 10)
    English (Collectr), rows: Collectr price (SGD), Change (SGD), Change, Period (skip the row when the page states none), TCGplayer listing (SGD), PSA 10 vs raw, PSA 9 vs raw
    | Measure | Value |
    Basis: <raw or the PSA grade the rows measure, then the site, for example `PSA 10, SnkrDunk` or `raw, Collectr`>.

    ### 4. Grading (GemRate, PSA)
    | Population | Gems | Gem rate | Past month | Month before | Change |

    ### Summary
    - **Case for buying:** <one sentence>
    - **Case for selling:** <one sentence>
    - **The card:** <one sentence>
    - **Price range:**
      - PSA 10: SGD <low> (<site>) to SGD <high> (<site>), all sites, <n> prices
      - Raw: SGD <low> (<site>) to SGD <high> (<site>), all sites, <n> prices
    - **Median vs ask price:**
      - PSA 10: median SGD <median> (<site>) vs lowest ask SGD <ask> (<site>), ask <above or below> by SGD <difference>
      - Raw: median SGD <median> (<site>) vs grade A ask SGD <ask> (<site>), ask <above or below> by SGD <difference>

Cell rules:
- A grade with an ask and no sale prints `none` in the last-sold cell and `n/a` in the comparison cell.
- A figure that cannot be computed prints `n/a`. A figure that was not read prints `not read: <reason>`.
- Every "X vs Y" and Change cell is X / Y - 1, except "PSA 10 vs raw" and "PSA 9 vs raw", which are the plain ratio of that grade's price to the raw price, one decimal with `x`. Change and Period are quoted as the page shows them; Period shows only when the page states one; otherwise skip that row. Collectr price and TCGplayer listing are raw values as the page shows them; derive nothing from them. In section 4, Change = past month / month before - 1.
- Sales per day = PSA 10 sales in the sold list / days spanned. Window = `<n> sales, <d> days`. On SnkrDunk, raw means the condition grades A, B, C and D; the raw median and range cover every raw sale in the sold list.

## Summary rules

- Three argument lines (buying, selling, the card), each one sentence using only numbers shown in sections 1 to 4, then two derived items, Price range and Median vs ask price. Median vs ask price compares the all-sites median (its site named, as for the range) with the ask for that grade group: for PSA 10 the lowest SnkrDunk PSA 10 ask, for raw the SnkrDunk grade A ask only (no other grade). Collectr's own price is not an ask. For an English card, which has no SnkrDunk asks, the raw ask is the TCGplayer listing in Collectr's Shop panel and PSA 10 prints `none`. The difference is the ask minus the median, taken from the two printed prices, in SGD with no percentage. The main session derives the two items itself, never an agent: run `sh derive.sh <JPY per SGD> <USD per SGD>` from this skill's folder and copy its figures and sites. Feed it one stdin line per site and group: `P10 SnkrDunk JPY 10500 10000 ...`, `P10 eBay USD 99 60` (CardLadder sales use their marketplace as the site), `P10 Collectr SGD 79`, `RAW ...`, and the asks as `ASKP10 SnkrDunk JPY 10500` and `ASKRAW SnkrDunk JPY 2900`. It converts to SGD and prints the n, range, median and ask difference, each with its site; derive nothing by hand. For a Japanese card it also prints `JPY` lines (the SnkrDunk yen median and range, and the PSA 10 ask against that median) for section 3. Each item has a PSA 10 sub-line and a raw sub-line, and each sub-line gives only the all-sites figure and how many prices it covers, with the site named next to every price (a range is `low to high`; a sale's site is its marketplace, for example eBay; a median that is the mean of two prices from different sites names both sites). Sources: Collectr is the single price on its DATA line, so its range and median are that one price; SnkrDunk is its DATA sold list; CardLadder is the section 2 rows of that grade (raw has none, because those rows are graded). All sites pools every price above, counting Collectr's price once. A site that was not read, or has no price for that grade, is left out of the pool and named in one note under the Summary. Quote how many sales a capped list covers; SnkrDunk's sales-history page appears to list at most 20 sales per grade. Quote every price in SGD only: convert any yen figure at the rate from step 2 to two decimals, and never put two currencies in one sentence. Name the site beside every price, for example "an eBay sale of SGD 46.02" or "the Collectr price of SGD 6.48". For a sale the site is the marketplace on the Marketplace line, not CardLadder. State the argument, never a verdict: the words "buy", "sell" and "hold" never appear as advice. Case for buying: what in the tables favours buying (a TCGplayer listing price under the Collectr price, an ask under recent sales). Case for selling: what favours selling (a falling price, a rise in grading volume, a wide gap between sales). The card: a general fact (population, gem rate, grade premium).
- A figure whose period or meaning the page does not state is quoted with that caveat, for example "over an unstated period".
- If no measure favours a side, print `none in the data`. If the inputs are missing, print `n/a, needs <what is missing>`.
- Before printing, draft the three sentences, then invoke the why skill once on each sentence, as three separate checks. The two derived items are checked by the command that computes them, so the why skill does not run on them. Each check recomputes every number in the sentence from the tables above and confirms any period or meaning caveat. It makes no new page reads. Print only the corrected sentences, never the why question or answer. A sentence the check finds unsupported is replaced by `none in the data` or `n/a, needs <what is missing>`.
