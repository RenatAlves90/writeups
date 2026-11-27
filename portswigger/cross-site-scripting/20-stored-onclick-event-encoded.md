# LAB: Reflected XSS into an onclick event with angle brackets and double quotes HTML-encoded and single quotes backslash-escaped

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |         25                                                                                                                        |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-escaped) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a website feature where input is reflected inside an inline `onclick` event handler, angle brackets (`<`/`>`) and double quotes (`"`) are HTML-encoded, and single quotes (`'`) are backslash-escaped (`\'`), executing `alert()`.

## 2. Surface

- URL query parameter reflected directly inside an HTML event handler attribute (e.g., `<a href="..." onclick="var track = trackSearch('USER_INPUT');">`).
- Server-side encoding and escaping filters:
  - Angle brackets (`<` -> `&lt;`, `>` -> `&gt;`).
  - Double quotes (`"` -> `&quot;`).
  - Single quotes (`'` -> `\'`).
- HTML attribute & JavaScript execution context: Input is processed by the browser's HTML attribute parser **before** being passed to the JavaScript execution engine.

## 3. Hypothesis

If user input is reflected inside an inline HTML event handler (`onclick="..."`) delimited by double quotes, and the server escapes single quotes (`'`) with a backslash (`\'`) while encoding double quotes and angle brackets, an attacker can leverage **HTML Entity Encoding** (`&apos;` or `&#39;`). 

Because HTML attribute parsing occurs prior to JavaScript execution, the browser decodes HTML entities inside attribute values *before* evaluating the script context. Pre-encoding single quotes as `&apos;` or `&#39;` bypasses backend backslash-escaping filters completely, decoding into a raw single quote (`'`) in the DOM context to break out of the JavaScript string literal.

## 4. Payload that worked

Request:
```http
POST /post/comment HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 175
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
Referer: https://<host>.web-security-academy.net/post?postId=4
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

csrf=ZXP9UeFC1cyhCJ9HgsI8LsPOOcrRvzBJ&postId=3&comment=test&name=test&email=wiener%40normal-user.net&website=https%3A%2F%2Ftest%40test.com%3F%26apos%3B-alert%281%29-%26apos%3B
```
Response:
```http
HTTP/2 302 Found
Location: /post/comment/confirmation?postId=3
X-Frame-Options: SAMEORIGIN
Content-Length: 0

<a id="author" href="https://test@test.com?'-alert(1)-'" onclick="var tracker={track(){}};tracker.track('https://test@test.com?'-alert(1)-'');">test</a>
```
## 5. Why it works

Analyzing the HTML response revealed that input passed to the search parameter is reflected directly inside an inline JavaScript function call within an HTML `onclick` event attribute:

```html
<a href="#" onclick="var track = trackSearch('USER_INPUT');">
```

While the backend application attempts to secure the single-quoted string by escaping single quotes (`'` -> `\'`), double quotes (`" -> &quot;`), and angle brackets (`<`/`>`), it fails to encode or filter HTML entities like `&apos;` (or `&#39;`).

Understanding the browser's dual-parsing architecture enables the bypass:
1. When input containing `&apos;` is properly URL-encoded (`%26apos%3B`) during HTTP transmission, the backend reflects the literal sequence `&apos;` into the `onclick` attribute inside the HTTP response.
2. The browser's **HTML parser** processes the attributes of the `<a>` tag **before** handing execution over to the JavaScript engine.
3. Because `&apos;` resides within an HTML attribute context (`onclick="..."`), the HTML parser automatically converts `&apos;` back into a literal single quote (`'`), bypassing the backend's initial backslash-escaping filter (`\'`).
4. Injected as `&apos;-alert(1)-&apos;`, the decoded payload resolves in JavaScript context to `'-alert(1)-'`. The hyphen operators (`-`) evaluate the `alert(1)` call as part of a valid mathematical expression, breaking out of the string boundary without generating a syntax error.

## 6. What I tried that failed

- Submitting raw `&apos;` directly via Burp Suite without URL-encoding the ampersand (`%26`) failed because the web server parsed `&` as an HTTP parameter delimiter, truncating the payload.
- Supplying unencoded single quotes (`'`) resulted in `\'`, which kept the quote trapped inside the JavaScript string literal.
- Attempting HTML tag breakouts (`</script>`) failed because angle brackets were converted to `&lt;` and `&gt;`.
- Rule extracted: When user input is reflected inside an inline HTML event handler attribute (`onclick`, `onmouseover`), escaping single quotes with backslashes is useless. Pre-encoding single quotes as HTML entities (`&apos;` / `&#39;`) and URL-encoding the payload (`%26apos%3B`) ensures proper delivery and DOM-level decoding prior to JS execution.
## 7. In a real target (bounty translation)

- Where it shows up: Dynamic tracking parameters, analytics event triggers, button click handlers, and social share buttons embedded directly in HTML event attributes (`onclick`, `onmouseover`, `onsubmit`).
- Quick detection: Test input containing HTML entities (`&apos;` or `&#x27;`) within event attributes. Inspect the DOM to confirm if the browser decodes entities prior to JavaScript execution.
- Impact: Reflected XSS execution when a victim interacts with the targeted element (or via automated focus triggers), leading to session hijacking or unauthorized action execution.
- In the report: Detail the dual-parsing behavior (HTML attribute parsing vs. JS string escaping order), demonstrate the HTML entity encoding bypass against backslash filters, and provide reproduction steps.

## 8. Bypass / variants noticed

- Using numeric HTML entity encoding instead of named entities: `&#39;-alert(1)-&#39;` or hexadecimal `&#x27;-alert(1)-&#x27;`.
- Using alternative arithmetic operators or commas to execute functions within the unquoted context: `&apos;;alert(1);//` or `&apos;+alert(1)+&apos;`.

## 9. Takeaway

Escaping single quotes with backslashes (`\'`) inside inline HTML event handler attributes is completely ineffective. Browsers decode HTML entities contained within HTML attribute values prior to passing the code to the JavaScript engine. Backend applications must strictly HTML-entity-encode all special characters (or use `&apos;` / `&#39;`) rather than relying on backslash escaping inside HTML event attributes.
