# Agent C: last sold (section 2)

Read common.md and gemrate.md first. **Route:** on the card page run a script that finds the link whose host is `app.cardladder.com`, sets its target to `_self` and clicks it, so the page opens in your own tab. **Fallback:** click the `CardLadder` link by coordinates; it opens a new tab, so use the tab id the tool reports. It lists up to the 5 most recent sales. The text is not selectable, so take a screenshot (zoom if needed) and read date, type, price and grade (from the listing title), and the marketplace named on each listing (for example eBay). The price is shown with `$`; treat it as USD. If you are sent to a sign-in page, print `not read: sign-in needed`.

Return only this section (SGD = USD / (USD per SGD) from the rates you were given, two decimals; rows lowest to highest grade (raw, PSA, BGS, CGC), then newest first; at most 5 rows):

```
### 2. Last sold (CardLadder)
| Grade | Date | Type | Price (USD) | Price (SGD) |
Marketplace: <name shown on the listings; if they differ, name each after its grade>.
```
