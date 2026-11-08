---
name: box
description: Rephrase Claude's last reply as a data path only, from config to output or UI, treating the code as a black box. Triggers: /box, json, yaml, csv, config, schema, overrides, data, dataset, record, field, payload, data store, data flow.
---

# box

1. Re-read your last reply. If a topic is given, keep only that part.
2. Redraw it as a data path from config to output or UI in the app, with the
   code between them as one box label. Do not describe it. Use a diagram, or
   a before and after table of field, value and type.
3. `+` or `-`, repeated for more: each symbol adds or removes one data state
   between box labels. Mixed symbols count as the net. Take the current level
   from your last /box output; default is one label. Never go below one label
   or past the real data states.
4. If drawing the path needs a choice, put it to Jev before picking.
5. Pick the one claim in the draft most likely to be wrong or unverified.
   Check it with a real read or command. If it is wrong, fix the draft.
6. Review the final output with ponytail and cut anything that is not data.
   If step 5 corrected a claim, add one line after the output:
   "Corrected: <claim>".

Do not:
- Mix unlike things in one table column, such as a key, a config change and
  a file version.
- Say a check ran when it did not.

Make no edits.
