# LAB: Reflected XSS into a nested object with double quotes HTML-encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | APPRENTICE                                                                                                                   |
| **Date**                    | 2026-11-25                                                                                                                     |
| **Time**                    |           15                                                                                                                      |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-href-attribute-double-quotes-html-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on an application where user input is reflected inside an `href` attribute and double quotes are HTML-encoded, executing `alert()`.

## 2. Surface

- URL query parameter reflected inside anchor tags (e.g., `backLink` or dynamic navigation parameters).
- Server-side encoding mechanism converting double quotes (`"` -> `&quot;`).
- HTML reflection context: Input reflected directly as the target URL of an `href` attribute (e.g., `<a href="USER_INPUT">`).

## 3. Hypothesis

If user input is reflected directly inside an `href` attribute and double quotes are HTML-encoded—preventing attribute boundary breakout—an attacker can inject a pseudo-protocol vector directly into the URL scheme (`javascript:alert(1)`). Because the payload forms the value of the `href` attribute itself, executing JavaScript does not require breaking out of quotes or injecting new HTML tags.

## 4. Payload that worked

Request:
```http
POST /post/comment HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 126
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://<host>.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://<host>.web-security-academy.net/post?postId=1
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

csrf=csrf&postId=1&comment=test&name=test&email=ut5e7ty7%40anonaddy.me&website=javascript:alert(1)
```
Response:
```http
HTTP/2 302 Found
Location: /post/comment/confirmation?postId=1
X-Frame-Options: SAMEORIGIN
Content-Length: 0

---
<section class="comment">
  <p>
    <img src="/resources/images/avatarDefault.svg" class="avatar">
    <a id="author" href="javascript:alert(1)">
      test
    </a>
      | 25 November 2026
    </p>
    <p>test</p>
    <p>
  </p>
</section>
```
## 5. Why it works

Analyzing the client-side JavaScript and API endpoints revealed a disconnect between client-side input validation and server-side link rendering:

1. The front-end interface enforced client-side validation rules (such as URL format checks) on the "Website" input field within the UI form, rejecting non-standard URL strings like `javascript:alert(1)`.
2. Bypassing the front-end form validation by submitting the JSON payload directly to the backend API endpoint (`POST /post/comment`) succeeded because the API lacked server-side protocol/scheme validation.
3. The server stored the unvalidated `javascript:alert(1)` input and reflected it directly as the target value of an anchor tag's `href` attribute (`<a href="javascript:alert(1)">User Website</a>`).
4. Although double quotes (`"`) were HTML-encoded by the server (preventing attribute boundary breakout via `"`), injecting a `javascript:` pseudo-protocol URL does not require breaking out of quotes. When a victim clicks the dynamic link, the browser executes the `javascript:` URI directly in the victim's session context.

## 6. What I tried that failed

- Attempting to submit `javascript:alert(1)` directly through the web form failed due to client-side JavaScript validation blocking non-HTTP/HTTPS schemes.
- Submitting HTML entity escapes (such as `&quot;`) and URL-encoded variants (`%22`) to break out of the `href="..."` attribute string failed because the backend safely encoded double quotes, reflecting them literally inside the attribute value and triggering input validation errors.
- Rule extracted: Client-side validation is completely trivial to bypass by sending requests directly to the backend API. When input reflects inside an `href` attribute, quote-encoding defenses are ineffective against `javascript:` pseudo-protocol schemes; full URL/protocol validation must be performed server-side.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic "Back" buttons, user profile website fields, dynamic redirect links, and breadcrumb navigation links.
- Quick detection: Inspecting link destinations (`href` values) where query parameters or user profile inputs are reflected as link targets.
- Impact: Reflected XSS execution when a user clicks the affected link, enabling session hijacking, malicious redirects, or targeted credential prompt injection.
- In the report: Document the reflected `href` attribute context, note the lack of scheme/protocol validation (allowing `javascript:`), and provide the reproduction link.

## 8. Bypass / variants noticed

- Using alternative pseudo-protocols like `data:text/html;base64,...` or `vbscript:` (in legacy context) to execute script contexts.
- Obfuscating the `javascript:` scheme using URL encoding or control characters within the scheme (e.g., `java&#x09;script:alert(1)` or `javascript:alert(document.cookie)`).

## 9. Takeaway

Encoding double quotes is insufficient when input is reflected directly inside link target attributes (`href`, `src`, `action`). Applications must restrict user-controlled URLs to safe protocols (`http`, `https`) via strict protocol validation before reflecting them as attributes.
