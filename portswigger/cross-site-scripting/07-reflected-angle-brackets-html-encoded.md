# LAB: Reflected XSS into attribute with angle brackets HTML-encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-25                                                                                                                     |
| **Time**                    |                   5                                                                                                              |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-attribute-angle-brackets-html-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-attribute-angle-brackets-html-encoded) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where input is reflected within an HTML attribute and angle brackets (`<` and `>`) are HTML-encoded, executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side encoding mechanism converting angle brackets (`<` -> `&lt;`, `>` -> `&gt;`).
- HTML reflection context: Input reflected directly inside an HTML element attribute value (e.g., `<input value="USER_INPUT">`).

## 3. Hypothesis

If user input is reflected directly inside an HTML attribute value and the application HTML-encodes angle brackets (`<` and `>`) but fails to encode or escape double quotes (`"`), an attacker can break out of the attribute value string using a double quote (`"`). By appending a valid event handler attribute (such as `onfocus` or `onmouseover`) and automated interaction attributes (such as `autofocus`), JavaScript code can be executed without needing to construct new HTML tags or use angle brackets.

## 4. Payload that worked

Request:
```http
GET /?search=%22+autofocus+onfocus%3Dalert%28document.domain%29+x%3D%22 HTTP/2
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
Referer: https://<host>.web-security-academy.net/?search=test%22+block
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 6526

<input type=text placeholder='Search the blog...' name=search value="" autofocus onfocus=alert(document.domain) x="">
```
## 5. Why it works

Analyzing the HTML response source revealed that user input passed to the search parameter was reflected directly inside an existing HTML tag's attribute value context:

```html
<input type="text" name="search" value="USER_INPUT">
```

Although the application HTML-encodes angle brackets (`<` to `&lt;` and `>` to `&gt;`), preventing the creation of new HTML tags (like `<script>`), it failed to encode double quotes (`"`). Injecting `" autofocus onfocus=alert(document.domain) x="` breaks out of the existing attribute boundary and constructs new, valid attributes on the host element:

```html
<input type="text" name="search" value="" autofocus onfocus=alert(document.domain) x="">
```

1. **The leading quote (`"`)**: Closes the original `value="` attribute prematurely, leaving the input tag open for additional attribute injection.
2. **`autofocus`**: Instructs the browser to automatically direct DOM focus to this `<input>` element as soon as the page finishes loading.
3. **`onfocus=alert(document.domain)`**: Binds the JavaScript payload to the `focus` event. Because `autofocus` immediately focuses the element, `onfocus` fires instantly upon page load without requiring any manual user interaction (such as clicking or hovering).
4. **The trailing `x="`**: Acts as a syntactic separator. When the original page template appends its own closing quote (`">`), it harmlessly completes the dummy attribute `x=""`, preventing an unclosed quote syntax error from breaking HTML parsing.

## 6. What I tried that failed

- Submitting standard HTML tags like `<script>alert(1)</script>` failed because the application converted `<` and `>` into `&lt;` and `&gt;`, reflecting the input as harmless raw text inside the `value` attribute.
- Injecting payloads without a trailing attribute placeholder (e.g., `" autofocus onfocus=alert(1)`) often results in broken HTML rendering because the application's remaining trailing double quote breaks attribute syntax.
- Rule extracted: When input is reflected inside an attribute and angle brackets are encoded but quotes are unescaped, you do not need to inject new tags. Closing the attribute string with `"` permits direct injection of event handlers (`onfocus`) combined with auto-triggering attributes (`autofocus`), while using a dummy trailing attribute (`x="`) safely absorbs the template's original closing quote.
## 7. In a real target (bounty translation)

- Where it shows up: Search input fields, user profile form fields, dynamic hidden inputs, and URL reflection parameters inside HTML attributes.
- Quick detection: Submit test input containing quotes and angle brackets (e.g., `" test=' <>`) into form fields and audit the page source to check if quote delimiters remain unencoded inside attribute boundaries.
- Impact: Reflected XSS execution within victim sessions upon accessing crafted links or forms, enabling session token exfiltration, client-side dynamic alterations, or forced action execution.
- In the report: Document the attribute reflection context, point out the missing quote encoding validation, outline the event handler injection vector, and supply the reproduction link.

## 8. Bypass / variants noticed

- Using alternative event handlers combined with `autofocus`, such as `onfocusin` or `onblur` (if forced focus changes occur).
- Swapping double quotes for single quotes (`' autofocus onfocus=alert(1) x='`) if the target attribute boundary is delimited by single quotes.
- Replacing `autofocus` with `accesskey` tricks (e.g., `" accesskey="x" onclick="alert(1)" x="`) in scenarios where `autofocus` is stripped or restricted.

## 9. Takeaway

HTML-encoding only angle brackets is insufficient when user input is reflected inside HTML attributes. Applications must apply contextual encoding—specifically encoding quote characters (`"` to `&quot;` and `'` to `&#x27;`)—or use safe template frameworks that handle attribute escaping automatically.
