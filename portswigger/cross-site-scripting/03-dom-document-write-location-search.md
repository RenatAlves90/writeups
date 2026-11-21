# LAB: DOM XSS in document.write sink using source location.search

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-21                                                                                                                     |
| **Time**                    |       10                                                                                                                          |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-document-write-sink](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink)         |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack by identifying a client-side execution path where data read from `location.search` (source) flows into `document.write()` (sink) to execute `alert()`.

## 2. Surface

- URL query parameters (`/search?search=...`).
- Client-side JavaScript executing in the browser DOM.
- DOM Sink: `document.write(...)` call within the page script handling the search query.

## 3. Hypothesis

If client-side JavaScript reads the unencoded `search` parameter from `location.search` and passes it directly into a `document.write()` call to construct HTML elements (such as an `<img>` tag), injecting syntax-breaking characters (e.g., closing quotes/tags) will allow breakout from the attribute context to execute arbitrary JavaScript.

## 4. Payload that worked

Request:
```http
GET /?search=+%27%22%3E%3Cscript%3Ealert%28%27%27%29%3C%2Fscript%3E HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://<host>.web-security-academy.net/?search=+%27%22%3E%3Cscript%3Ealert%28%27%27%29%3C%2Fscript%3E
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 6978
<img src="/resources/images/tracker.gif?searchTerms= '">
<script>alert('')</script>
```

## 5. Why it works

The target application uses a client-side JavaScript snippet that reads the unencoded `search` query parameter directly from `location.search` (source) and inputs it into a `document.write()` call (sink) to dynamically render an HTML `<img>` element on the page. Because the user input is inserted directly inside the `src` attribute of the generated `<img>` tag without sanitization, supplying standard HTML tags like `<script>` alone fails to execute as valid markup. 

Injecting the payload `'"><script>alert('')</script>` uses the single quote `'` to break out of the `src` attribute value and the closing bracket `>` to close the dynamically generated `<img>` tag prematurely. This forces the browser DOM to parse the subsequent string as a standalone, valid `<script>` element, executing `alert('')` within the client DOM context.

## 6. What I tried that failed

- Submitting a standard `<script>alert('')</script>` payload directly in the search input failed to trigger execution. Inspection of the page DOM via browser DevTools showed that the input was being injected inside the `src` attribute of an `<img>` tag constructed via `document.write()`, causing the script tag to be treated as part of the image URL attribute rather than executable markup.
- Rule extracted: When dealing with DOM-based XSS, always inspect the DOM structure and source code to identify how input is parsed within the sink before crafting breakout characters (`'`, `"`, `>`, `/`).
  
## 7. In a real target (bounty translation)

- Where it shows up: Dynamic client-side routing, search parameter handling via front-end frameworks, or legacy scripts rendering URL parameters directly into the DOM using dangerous sinks (`document.write`, `innerHTML`, `eval`).
- Quick detection: Search the page JavaScript sources for references to `location.search`, `location.hash`, or `document.URL`, and trace whether those values are passed without sanitization into DOM-writing sinks.
- Impact: Execution of arbitrary JavaScript on the client side without requiring backend reflection, enabling session manipulation or client-side data theft.
- In the report: Identify the exact client-side source and sink, document the vulnerable JavaScript snippet, show the un-sanitized DOM data flow, and provide the working PoC URL.

## 8. Bypass / variants noticed

- Escaping the attribute context using inline event handlers instead of breaking out with a new tag (e.g., `' onerror='alert('')` or `' onload='alert('')`).
- Exploiting alternate sink patterns where `document.write` handles single vs. double quotes, adjusting the breakout delimiter accordingly.
  
## 9. Takeaway

Client-side JavaScript must avoid writing untrusted data directly into unsafe HTML sinks like `document.write()`. Dynamic DOM manipulation should use safer APIs such as `textContent` or framework-native text binding to prevent browser execution of injected markup.
