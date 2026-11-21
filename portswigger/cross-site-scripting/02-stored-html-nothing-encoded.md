# LAB: Stored XSS into HTML context with nothing encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-21                                                                                                                     |
| **Time**                    |                             2                                                                                                    |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-html-context-nothing-encoded](https://portswigger.net/web-security/cross-site-scripting/stored/lab-html-context-nothing-encoded) |

## 1. Objective

Submit a comment containing a malicious payload that triggers the `alert()` function in the browser of any user who views the blog post page.

## 2. Surface

- Comment submission form (`POST /post/comment`).
- Input fields: `comment`, `author`, `email`, `website`.
- Reflection point: Blog post page where submitted comments are stored in the backend database and dynamically rendered in the HTML body.

## 3. Hypothesis

If the application stores the user-supplied comment input directly into the database without HTML sanitization or entity encoding, injecting executable tags (such as `<script>`) will result in persistent JavaScript execution whenever the post page is viewed.

## 4. Payload that worked

Request:
```http
POST /post/comment HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 152
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
Referer: https://<host>.web-security-academy.net/post?postId=8
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

csrf=FuN2sdVxHwVdRmhANIot9435PapcSklc&postId=8&comment=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E&name=test&email=wiener%40normal-user.net&website=
```
Response:
```http
HTTP/2 302 Found
Location: /post/comment/confirmation?postId=8
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```
## 5. Why it works

The backend application accepts user input from the comment submission form (`POST /post/comment`) and stores it directly into the database without performing any server-side HTML entity encoding or input sanitization. When the blog post page is retrieved, the stored comment string is rendered dynamically into the HTML body. Because the raw string `<script>alert('xss')</script>` is delivered to the victim's browser, the rendering engine interprets the tag as executable code rather than plain text, running the script persistently across page reloads.

## 6. What I tried that failed

- Inserting the basic payload `<script>alert('xss')</script>` into the `comment` field executed successfully on the first attempt without triggering WAF rules or client-side filtering.
- Rule extracted: Before testing complex obfuscation or bypass techniques on stored forms, always test standard tags to check if baseline HTML encoding is applied at output rendering.
  
## 7. In a real target (bounty translation)

- Where it shows up: Comment forms, user profile fields, support ticket messaging, feedback widgets, or internal admin dashboard logs.
- Quick detection: Submit test strings with HTML syntax (e.g., `test"'><i>x1</i>`) into persistent forms and reload the rendering page to check raw HTML source encoding.
- Impact: Persistent browser code execution affecting any user or administrator viewing the page. Can lead to session theft, stored worms, or admin panel takeover.
- In the report: Document the endpoint accepting the stored input, the rendering view URL, the raw HTTP response showing unencoded reflection, and the PoC triggering `alert()`.

## 8. Bypass / variants noticed

- Testing secondary input fields in the same form (`author`, `email`, `website`) to check for inconsistent field-level encoding (e.g., payloads in `website` rendered inside `href` attributes vs. `comment` in HTML body).
- Utilizing alternate HTML tags and inline event handlers (e.g., `<img src=x onerror=alert('xss')>` or `<svg onload=alert('xss')>`) to achieve execution if explicit `<script>` tags are blacklisted by backend filters.
  
## 9. Takeaway

All user-supplied inputs saved to databases and later rendered in HTML body contexts must be strictly HTML-entity encoded upon output rendering to ensure stored payloads are treated purely as static text data rather than executable markup code.
