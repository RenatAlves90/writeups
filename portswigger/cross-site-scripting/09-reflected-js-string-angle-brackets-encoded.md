# LAB: Reflected XSS into a JavaScript string with angle brackets HTML-encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | APPRENTICE                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |                5                                                                                                                 |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-string-angle-brackets-html-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-html-encoded) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where user input is reflected inside a JavaScript single-quoted string literal, and angle brackets (`<` and `>`) are HTML-encoded, executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side encoding mechanism converting angle brackets (`<` -> `&lt;`, `>` -> `&gt;`).
- Inline JavaScript reflection context: Input reflected directly inside a `<script>` tag within a single-quoted string literal (e.g., `var searchTerms = 'USER_INPUT';`).

## 3. Hypothesis

If user input is reflected inside a single-quoted JavaScript string literal inside a `<script>` block and the application HTML-encodes angle brackets (`<` and `>`)—preventing `</script>` tag breakout—but fails to encode or escape single quotes (`'`) or backslashes (`\`), an attacker can break out of the string literal using a single quote (`'`), concatenate or sequence JavaScript expressions using operators (such as `-`, `+`, or `;`), and comment out the remainder of the script line (`//`) to execute arbitrary code within the existing inline script context.

## 4. Payload that worked

Request:
```http
GET /?search=%27%3B+alert%28%29%3B%2F%2F HTTP/2
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
Referer: https://<host>.web-security-academy.net/?search=alert%281%29
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 3587
<script>
  var searchTerms = '';
  alert();//';
  document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>
```
## 5. Why it works

Analyzing the page source revealed that user input is reflected directly inside a single-quoted JavaScript string literal within an inline `<script>` block:

```html
<script>
    var searchTerms = 'USER_INPUT';
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>
```

While the application HTML-encodes angle brackets (`<` -> `&lt;` and `>` -> `&gt;`), preventing `</script>` tag breakout vectors, it fails to escape single quote delimiters (`'`) or backslashes (`\`).

Injecting the payload `'; alert(1); //` operates directly within the existing JavaScript context:
1. The leading single quote (`'`) terminates the `searchTerms` string literal boundary.
2. The semicolon (`;`) completes the `var searchTerms = '';` assignment statement.
3. `alert(1);` appends a distinct JavaScript expression that executes immediately when the inline script block is evaluated by the browser.
4. The trailing double slashes (`//`) comment out the remaining code on the line (the original closing single quote and semicolon), preventing a syntax error that would otherwise disrupt script execution.

## 6. What I tried that failed

- Attempting to close the script block using `</script><img src=1 onerror=...>` failed because the backend converted `<` and `>` into `&lt;` and `&gt;`, resulting in a literal string output rather than breaking out of the HTML tag.
- Testing quotes without statement terminators or comment flags (e.g., `' alert(1)`) resulted in JavaScript parsing syntax errors (`Uncaught SyntaxError`), preventing script execution.
- Rule extracted: When angle brackets are HTML-encoded but single quotes are unescaped inside an inline JavaScript string literal, HTML tag breakout is impossible. Break out of the JavaScript string assignment directly using `'`, terminate the statement with `;`, append the payload expression, and neutralize the rest of the original script line using `//`.

## 7. In a real target (bounty translation)

- Where it shows up: Search result counters, dynamic page state tracking variables, and inline configuration objects embedded inside `<script>` blocks.
- Quick detection: Pass test strings containing single quotes, backslashes, and operators (`'-alert(1)-'`) to verify if JavaScript syntax breaking occurs inside the inline script block without HTML tag injection.
- Impact: Reflected XSS execution within victim sessions upon accessing crafted links, enabling session token exfiltration, client-side DOM manipulation, or forced action execution.
- In the report: Document the inline script reflection context, show the missing single-quote escaping validation, outline the JavaScript syntax breakout PoC, and supply the reproduction URL.

## 8. Bypass / variants noticed

- Using binary/string operators to concatenate execution vectors within the same statement: `'-alert(1)-'` or `';alert(1)+'` (without needing trailing comments if syntax balances out).
- Using backticks (``` `alert(1)` ```) or template literals if single quotes were filtered but backticks remained unescaped in modern JS engines.

## 9. Takeaway

HTML-encoding angle brackets protects against HTML tag breakout (`</script>`), but does not protect against XSS when input is reflected directly inside an inline JavaScript string literal. Backend applications must safely escape quote delimiters and backslashes or use standard data serialization formats like `JSON.stringify()` / HTML-encoded data attributes to pass dynamic data to JavaScript contexts safely.
