#!/bin/sh
# Derives the scan Summary's "Price range" and "Median vs ask price" figures,
# and the yen figures for a Japanese card's section 3.
# usage: derive.sh <JPY per SGD> <USD per SGD> < price lines
# line:  <GROUP> <site> <JPY|USD|SGD> <price> [<price> ...]
#   GROUP is P10 (PSA 10 sold), RAW (raw sold), ASKP10 or ASKRAW (asks; the lowest is used)
# ponytail: insertion sort, fine for the few dozen prices a scan has; the JPY lines cover SnkrDunk only.
awk -v jpy="$1" -v usd="$2" '
function sgd(cur, v) { return cur == "JPY" ? v / jpy : cur == "USD" ? v / usd : v }
function fmt(x) { return sprintf("%.2f", x) }
function both(a, b) { return a == b ? a : a " and " b }
function sortg(g,   i, j, tv, ts) {
  for (i = 2; i <= n[g]; i++) {
    tv = val[g, i]; ts = src[g, i]; j = i - 1
    while (j >= 1 && val[g, j] > tv) { val[g, j + 1] = val[g, j]; src[g, j + 1] = src[g, j]; j-- }
    val[g, j + 1] = tv; src[g, j + 1] = ts
  }
}
function jsort(g,   i, j, tv) {
  for (i = 2; i <= jn[g]; i++) {
    tv = jv[g, i]; j = i - 1
    while (j >= 1 && jv[g, j] > tv) { jv[g, j + 1] = jv[g, j]; j-- }
    jv[g, j + 1] = tv
  }
}
{
  for (i = 4; i <= NF; i++) {
    n[$1]++; val[$1, n[$1]] = sgd($3, $i); src[$1, n[$1]] = $2
    if ($3 == "JPY" && $2 == "SnkrDunk") { jn[$1]++; jv[$1, jn[$1]] = $i + 0 }
  }
  if ($1 == "ASKP10" && $3 == "JPY" && (!ask10 || $4 + 0 < ask10)) ask10 = $4 + 0
}
END {
  for (k = 1; k <= 2; k++) {
    g = (k == 1) ? "P10" : "RAW"
    if (!n[g]) { print g, "none"; continue }
    sortg(g); c = n[g]
    if (c % 2) { m = val[g, (c + 1) / 2]; ms = src[g, (c + 1) / 2] }
    else { m = (val[g, c / 2] + val[g, c / 2 + 1]) / 2; ms = both(src[g, c / 2], src[g, c / 2 + 1]) }
    med[g] = fmt(m)
    printf "%s n=%d range %s (%s) to %s (%s) median %s (%s)\n", g, c, fmt(val[g, 1]), src[g, 1], fmt(val[g, c]), src[g, c], med[g], ms
  }
  for (k = 1; k <= 2; k++) {
    g = (k == 1) ? "ASKP10" : "ASKRAW"; b = (k == 1) ? "P10" : "RAW"
    if (!n[g] || !n[b]) { print g, "none"; continue }
    sortg(g); a = fmt(val[g, 1]); d = a - med[b]
    printf "%s ask %s (%s) vs median %s: ask %s by %s\n", g, a, src[g, 1], med[b], (d >= 0) ? "above" : "below", fmt((d >= 0) ? d : -d)
  }
  for (k = 1; k <= 2; k++) {
    g = (k == 1) ? "P10" : "RAW"
    if (!jn[g]) continue
    jsort(g); c = jn[g]
    jm[g] = (c % 2) ? jv[g, (c + 1) / 2] : (jv[g, c / 2] + jv[g, c / 2 + 1]) / 2
    printf "JPY %s n=%d median %s range %s - %s\n", g, c, jm[g], jv[g, 1], jv[g, c]
  }
  if (jm["P10"] && ask10) printf "JPY ASKP10 %s vs median %s: %+.1f%%\n", ask10, jm["P10"], (ask10 / jm["P10"] - 1) * 100
}'
