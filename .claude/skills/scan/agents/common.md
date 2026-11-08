# Rules for every scan agent

You are given: the card fields, a search query, the rates and one tab id. Read this file and your own agent file in one step (two Read calls in the same message).

- Read only. Never sign in, buy, bid, message or change anything on any site. Stop at a bot challenge or sign-in page and print `not read: <reason>` for that source.
- Never guess. A figure that was not read prints `not read: <reason>` in its own cell.
- You work alone: never wait for, or read from, another agent.
- When several candidates agree, ask the jev skill to pick. Accept a pick strictly above 0.6. Otherwise the match is `not matched`.
- Compute every SGD conversion and every percentage with a shell command (awk), never in your head, and round to two decimals (percentages to one). Mental rounding was wrong by one cent in earlier runs.
- The shell tool is named `Bash` (capital B); a lowercase `bash` fails.
- Browser: load the Chrome tools with one ToolSearch call and use the claude-in-chrome skill. Use only the tab id you were given and pass it as tabId on every call. Never close a tab and never call tabs_context_mcp or tabs_create_mcp (agents doing so removed each other's tab group). Chain navigate, a 3 second wait, then find or get_page_text in one browser_batch call. Pages load late: wait until the price or population appears.
- Each page has a route and a fallback in your file. Use the route. If the page shows an error or the expected text is missing, use the fallback once, then print `not read: <reason>`. Prefer navigate, get_page_text, coordinate clicks and page scripts over `find`: `find` is a model call and fails when usage runs out. Never print a link that holds a query string in a script result (the tool blocks it); click it instead.
- Return only the text your own file says to return, nothing else.
