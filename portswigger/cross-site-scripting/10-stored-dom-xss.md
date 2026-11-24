# LAB: Stored DOM XSS

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-24                                                                                                                     |
| **Time**                    |                         4                                                                                                      |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-dom-xss-stored](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-stored)                   |

## 1. Objective

Perform a Stored DOM Cross-Site Scripting (XSS) attack on a blog comment section by exploiting how stored comment data is rendered client-side via JavaScript, executing `alert()`.

## 2. Surface

- Blog comment submission form (`POST /post/comment`).
- Client-side JavaScript fetching and rendering stored comments into the DOM.
- DOM Sink: `innerHTML` or similar unsafe DOM manipulation sink handling user-controlled data retrieved from the database.

## 3. Hypothesis

If the backend stores comment content containing raw or partially sanitized HTML and client-side JavaScript fetches these comments via an API/XHR call and inserts them into the DOM using an unsafe sink (such as `innerHTML`), injecting an HTML vector with an inline event handler (e.g., `<img src=x onerror=...>`) will trigger JavaScript execution whenever the comment is loaded and rendered by a victim's browser.

## 4. Payload that worked

Request:
```http
GET /post/comment?postId=10 HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://<host>.web-security-academy.net/post?postId=10
Accept-Encoding: gzip, deflate, br
Priority: u=1, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 1888

[{"avatar":"","website":"","date":"2026-11-24T16:31:06.622447264Z","body":"<><img src=x onerror=alert(1)>","author":"<><img src=x onerror=alert(1)>"}]
```
## 5. Why it works

Analyzing the client-side JavaScript source revealed a custom sanitization function responsible for escaping user input before rendering comments dynamically into the DOM:

```javascript
function escapeHTML(html) {
    return html.replace('<', '&lt;').replace('>', '&gt;');
}
```

The function uses standard string `.replace()` calls without global regular expression flags (`g`). As a result, only the **first occurrence** of `<` and `>` in the input string is converted to HTML entities (`&lt;` and `&gt;`), leaving all subsequent angle brackets unescaped.

When submitting the payload `<><img src=x onerror=alert(1)>`:
1. The initial dummy container `<>` matches the single-replacement criteria and is sanitized to `&lt;&gt;`.
2. The remaining payload `<img src=x onerror=alert(1)>` bypasses escaping entirely and is written unencoded into an unsafe DOM sink (such as `innerHTML`).
3. The browser attempts to load the image from an invalid source `x`, triggering the `onerror` event handler and executing `alert(1)` within the victim's session context.

## 6. What I tried that failed

- Inspecting the comment section source code identified the custom `escapeHTML()` client-side sanitization function.
- Submitting standard XSS vectors like `<script>alert(1)</script>` failed because the leading `<` and `>` were escaped to `&lt;script&gt;alert(1)</script>`, preventing script tag execution.
- Testing `<><script>alert(1)</script>` successfully bypassed the initial sanitization check (yielding `&lt;&gt;<script>alert(1)</script>`), but modern browsers do not execute inline `<script>` tags injected dynamically into the DOM via `innerHTML`.
- Rule extracted: When input sanitization relies on non-global string replacement (`.replace('<', ...)`), prepending dummy breaking characters (`<>`) consumes the single-replacement pass. To achieve execution via dynamic DOM sinks like `innerHTML`, use HTML element vectors with event handlers (e.g., `<img onerror=...>`) rather than `<script>` tags.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic comment feeds, chat interfaces, user profile updates, and dashboard activity logs where content stored in a database is fetched via JSON/REST APIs and rendered dynamically on the front end.
- Quick detection: Submit identifiable markup patterns into input fields (e.g., comment boxes). Audit client-side scripts to observe how API responses containing user input are formatted and inserted into the page structure.
- Impact: Persistent client-side code execution. Every user viewing the affected page automatically executes the payload, enabling session hijacking, wormable XSS propagation, or targeted credential theft.
- In the report: Map the data flow from the stored API response to the client-side sink, identify the unescaped rendering function, and document the persistent execution PoC.

## 8. Bypass / variants noticed

- Prepending single unescaped brackets or dummy pairs to bypass single-pass sanitizers: `<><svg onload=alert(1)>` or `<<img src=x onerror=alert(1)>`.
- Leveraging alternative HTML5 event handlers if `onerror` is filtered by additional checks (e.g., `<><body onload=alert(1)>` or `<><input autofocus onfocus=alert(1)>`).

## 9. Takeaway

Stored data retrieved via API calls must be safely handled before being rendered into the DOM. Applications should prefer safe DOM APIs like `.textContent` over unsafe sinks like `.innerHTML`, or utilize robust client-side HTML sanitization libraries (such as DOMPurify) before inserting dynamic HTML.
