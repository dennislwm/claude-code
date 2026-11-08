# Agent D: Collectr prices (Japanese cards only; an English card is read by agent A)

Read common.md first. Assume the user is signed in to Collectr.

**Route:** open `https://app.getcollectr.com/?query=<query>`, take a screenshot, click the tile of the Japanese card (not an English card) that matches by number and set, at coordinates read from that screenshot, wait 3 seconds and read the card page with `get_page_text`. **Fallback:** `find` the tile and click its ref. If there is no Japanese match, print `not read: no Japanese listing found`. If the set code was not legible on the card, match on name and number. Read the ungraded price at the top of the page and the PSA 10 price. A sign-in page prints `not read: sign-in needed`.

Return only (SGD as the page shows it; you print no section):

```
COLLECTR raw (SGD): <price>
COLLECTR PSA 10 (SGD): <price>
COLLECTR page: <url>
```
(or `not read: <reason>` for any line)
