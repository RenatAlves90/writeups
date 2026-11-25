# LAB: Reflected XSS in canonical link tag

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-25                                                                                                                     |
| **Time**                    |               11                                                                                                                  |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-canonical-link-tag](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-canonical-link-tag)           |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on an application that reflects user input from the URL into a `<link rel="canonical">` tag, exploiting access keys and user interaction shortcuts to execute `alert()`.

## 2. Surface

- Request path and URL parameters reflected into the HTML `<head>` section inside a canonical link tag (e.g., `<link rel="canonical" href="CANONICAL_URL">`).
- HTML attribute reflection context: Input reflected directly inside the `href` attribute of a `<link>` tag.

## 3. Hypothesis

If the application reflects parts of the URL (path or query string) inside a `<link rel="canonical">` tag's `href` attribute without encoding single or double quotes, an attacker can break out of the attribute boundary (`href='...'` or `href="..."`). Since `<link>` elements are hidden by default, combining an unescaped quote breakout with the `accesskey` attribute and an event handler (such as `onclick`) allows script execution when the victim presses the specific access key shortcut sequence.

## 4. Payload that worked

Request:
```http
GET /?test=123%27onclick=%27alert(1)%27accesskey=%27x%27 HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 8817

<link rel="canonical" href='https://<host>.web-security-academy.net/?test=123'onclick='alert(1)'accesskey='x''/>
```
## 5. Why it works

Analyzing the HTML `<head>` response revealed that the application dynamically reflects the current URL path into a canonical link element:

```html
<link rel='canonical' href='[https://vulnerable-lab.web-security-academy.net/?PARAM'/](https://vulnerable-lab.web-security-academy.net/?PARAM'/)>
```

The application uses single quotes (`'`) to enclose the `href` attribute value. While double quotes and HTML entities were properly handled or sanitized, single quotes (`'`) were reflected unencoded.

Submitting the payload `'accesskey='x'onclick='alert(1)` in the URL path/query parameter manipulates the attribute structure:
1. The leading single quote (`'`) closes the opening `href='` attribute boundary.
2. `accesskey='x'` assigns a keyboard shortcut key (`x` or platform equivalent like `ALT+SHIFT+X` / `CTRL+OPTION+X`) to the `<link>` element.
3. `onclick='alert(1)'` attaches an event listener directly to the `<link>` element.
4. When a victim presses the designated shortcut key combination (`accesskey`), the browser shifts focus to and triggers a click event on the canonical `<link>` element, executing `alert(1)` within the victim's session context.

## 6. What I tried that failed

- Inspecting the HTML source confirmed the reflection context inside `<link rel='canonical' href='...'>` within the `<head>` tag.
- Testing double quotes (`"`), HTML entity variations (`&quot;`), and percentage encoding (`%22`) failed to break out of the attribute because the attribute boundary was delimited specifically by single quotes (`'`).
- Fuzzing multiple special characters (`/?test=`"'!@#$%^&*&*`) revealed that single quotes (`'`) reflected unescaped, allowing attribute injection.
- Attempting standard interaction-less payloads (like `autofocus onfocus=...`) failed because `<link>` elements reside inside `<head>` and are not rendered as standard visible/focusable DOM elements without key bindings.
- Rule extracted: When input is reflected inside single-quoted attributes (`href='...'`) of hidden elements like `<link>`, single quotes (`'`) break the attribute boundary. Because the element is non-renderable in the body flow, pairing `accesskey` with `onclick` forces an interaction trigger via keyboard shortcuts.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic SEO metadata implementations, canonical link tags, open graph meta tags, and alternate language link elements reflecting URL paths or query parameters.
- Quick detection: Injecting quotes (`'` and `"`) into the URL path or parameters and inspecting the HTML `<head>` section to check if attributes within `<link>` tags break open.
- Impact: Reflected XSS requiring specific keyboard interaction (access key triggering), enabling execution of client-side code on affected target pages.
- In the report: Document the URL reflection inside the canonical tag, detail the quote escape vulnerability, demonstrate the `accesskey` binding vector, and supply the reproduction URL.

## 8. Bypass / variants noticed

- Leveraging platform-specific shortcut triggers (e.g., `ALT+SHIFT+X` on Chrome/Windows or `CTRL+OPTION+X` on macOS) to invoke the `accesskey` execution vector.
- Combining `accesskey` with alternative event handlers such as `onfocus` or `onblur` if `onclick` is filtered by additional WAF rules.

## 9. Takeaway

URL reflection inside HTML header elements like `<link rel="canonical">` must be strictly HTML-attribute encoded. Applications should sanitize or URL-encode any user-supplied pathing or query parameters before incorporating them into metadata attributes.
