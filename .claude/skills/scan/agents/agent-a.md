# Agent A: prices (section 1; section 3 for an English card)

Read common.md first. SGD = JPY / (JPY per SGD) for yen, USD / (USD per SGD) for dollars, from the rates you were given.

## Japanese card: SnkrDunk

- **Route:** open `https://snkrdunk.com/search?keywords=<query>` and run a script that lists each `a[href*="/apparels/"]` link without `/used/` in its address, with its title (SnkrDunk links carry no query strings; cut each title to about 90 characters). Tiles link to `/apparels/<id>` and carry the title and a yen price. Drop duplicate ids. **Fallback:** `find` the tile links.
- A tile agrees when its title bracket `[CODE number/size]` has the same number (a range counts), the same code ignoring case and hyphens, and the same size when both give one. If the set code was not legible on the card, accept any code. Exactly one agreeing tile is the match. If none or several agree, use the jev rule among the first 30 tiles.
- Open `https://snkrdunk.com/apparels/<id>` and read the page text straight after navigate, with no fixed wait; if the page text has no prices, wait 3 seconds and read once more. Asks: each grade chip with its yen price. `出品待ち` means no listing. For the sold lists open `https://snkrdunk.com/apparels/<id>/sales-histories` and **Route:** run the script below; it returns the PSA 10 sales with dates and the raw A, B, C and D prices (its output has no `=` sign, because the tool blocks one). If it returns no rows, wait 3 seconds and run it once more. **Fallback:** read the page text. It appears to list at most 20 sales per grade. Raw means the condition grades A, B, C and D. The newest dates read `N日前` or `N時間前`; convert them with today's date from `date`.

```js
const L=document.body.innerText.split('\n').map(s=>s.trim()).filter(Boolean),o={};let g;for(const l of L){const m=l.match(/^状態(.+)の売買履歴$/);if(m)o[g=m[1]]=[];else if(g)o[g].push(l)}
const r=(k,d)=>{const a=(o[k]||[]).slice(3),x=[];for(let i=0;i+2<a.length&&/^[\d,]+$/.test(a[i+2]);i+=3)x.push(d?a[i]+' '+a[i+2]:a[i+2]);return x};
['PSA10','A','B','C','D'].map(k=>k+' '+r(k,k=='PSA10').join(' ')).join('\n')
```

Return, in this order (yen with thousands separators and no decimals, SGD two decimals, percentages one decimal with a sign; rows lowest to highest grade, raw first (D, C, B, A), then PSA, BGS, CGC, then newest first; at most 5 rows, extras in one `Also listed:` line):

```
### 1. Prices
| Grade | Ask (JPY) | Ask (SGD) | Last sold (JPY) | Ask vs last sold |
No listing: <grades with no ask>.
```
A grade with an ask and no sale prints `none` in the last-sold cell and `n/a` in the comparison cell. Ask vs last sold = ask / last sold - 1.

Then these lines, with plain numbers (no yen or dollar signs):

```
SET: <set code and set name the matched tile shows>
DATA PSA10 (JPY): <every PSA 10 sold price used, comma separated>
DATA RAW (JPY): <every raw A, B, C and D sold price used, comma separated>
WINDOW PSA10: <n> sales, <d> days
```
The window is the number of PSA 10 sales in the list and the days from its oldest to its newest sale. Do not compute any median, range, ask-vs-median or sales-per-day figure: the main session derives section 3 from the DATA lines. Do not return section 3.

## English card: Collectr (assume the user is signed in)

- **Route:** open `https://app.getcollectr.com/?query=<query>`, take a screenshot, click the tile that matches the printed number and set name, at coordinates read from that screenshot, wait 3 seconds and read the card page with `get_page_text`. **Fallback:** `find` the tile and click its ref. Read the Collectr price (the price at the top of the page), the change shown beside it, the TCGplayer price in the Shop panel and any graded prices. The Shop panel's TCGplayer row ("View all listings") shows one price; the page does not say whether it is the lowest listing. The eBay rows show no price. A sign-in page prints `not read: sign-in needed`. Note any period the page states for the change.

Return, in this order (SGD two decimals, changes exactly as the page shows them; rows lowest to highest grade, raw first; at most 5 rows, extras in one `Also listed:` line):

```
### 1. Prices
| Grade | Price (SGD) |
```
(a `Graded | not read: none listed` row when no graded price is shown)

```
### 3. Trend
| Measure | Value |
rows: Collectr price (SGD), Change (SGD), Change, Period (skip this row when the page states none), TCGplayer listing (SGD), PSA 10 vs raw, PSA 9 vs raw
Basis: raw, Collectr.
```
Collectr price and TCGplayer listing are raw values; derive nothing from them. PSA 10 vs raw and PSA 9 vs raw are the plain ratio of that grade's price to the raw price, one decimal with `x`.

Then three more lines:

```
SET: <set name Collectr shows>
DATA COLLECTR raw (SGD): <price>
DATA COLLECTR PSA10 (SGD): <price>
```
(or `not read: <reason>` for either)
