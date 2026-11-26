# LAB: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |                    5                                                                                                             |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where user input is reflected inside a JavaScript single-quoted string literal, angle brackets and double quotes are HTML-encoded, and single quotes are backslash-escaped (`\'`), executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side encoding and escaping mechanisms:
  - Angle brackets (`<` -> `&lt;`, `>` -> `&gt;`).
  - Double quotes (`"` -> `&quot;`).
  - Single quotes (`'` -> `\'`).
- Inline JavaScript reflection context: Input reflected directly inside a `<script>` tag within a single-quoted string literal (e.g., `var searchTerms = 'USER_INPUT';`).

## 3. Hypothesis

If user input is reflected inside a single-quoted JavaScript string literal and the application attempts to neutralize single quotes by prepending a backslash (`\'`), but fails to escape pre-existing user-supplied backslashes (`\`), an attacker can supply an explicit backslash (`\`) immediately preceding a single quote (`\'`). The server's escape routine turns the user's backslash into `\\'`, causing the server's added backslash to neutralize the user's backslash, leaving the single quote (`'`) unescaped in the final JavaScript execution context to break out of the string literal.

## 4. Payload that worked

Request:
```http
GET /?search=%27%5C%27%3Balert%28%29%3B%2F%2F%2F%2F HTTP/2
Host: 0a91009703451bb8813a3417004800a9.web-security-academy.net
Cookie: session=BjLET0gek8cVavnB4BW88TqzxC43ydEz
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
Referer: https://0a91009703451bb8813a3417004800a9.web-security-academy.net/?search=%27%5C%27%3Btest%2F%2F
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 3720
<script>
    var searchTerms = '\'\\';alert();////';
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>
```

## 5. Why it works

Analyzing the HTML response revealed that the backend attempts to neutralize single quotes by prepending a backslash (`\'`), while also HTML-encoding double quotes (`"`) and angle brackets (`<`, `>`). However, the application fails to escape user-supplied backslashes (`\`).

When submitting the payload `\';alert(1);//`, a backslash neutralization (escaping the escaper) occurs:
1. The user supplies `\` followed by `'`.
2. The server's sanitization routine sees the single quote `'` and prepends a backslash to it, transforming `\'` into `\\'`.
3. Inside the JavaScript string context, the first backslash escapes the second backslash (`\\` = literal `\`), which leaves the single quote (`'`) unescaped in the JS parser.
4. The unescaped single quote successfully terminates the `searchTerms` string literal boundary.
5. The semicolon (`;`) ends the assignment statement, allowing `alert(1);` to execute as a separate JavaScript expression.
6. The trailing `//` comments out the original closing quote and semicolon provided by the application template, preventing a JavaScript syntax error.

## 6. What I tried that failed

- Submitting single quotes alone (e.g., `';alert(1);//`) resulted in `\';alert(1);//` inside the script tag, keeping the single quote safely inside the string literal context as `\'`.
- Attempting HTML tag breakout (e.g., `</script>`) failed because angle brackets were converted to `&lt;` and `&gt;`.
- Fuzzing character sequences (`'`, `"`, `\"`, `\'`, `\\'`) identified that supplying an explicit backslash directly before a single quote caused the server's backslash filter to neutralize itself.
- Rule extracted: Prepending `\` to quotes without first escaping existing backslashes creates a classic backslash-escaping flaw. Supplying an odd number of backslashes before a quote neutralizes the server-side escape character, leaving the quote functional in the JavaScript context.## 7. In a real target (bounty translation)

- Where it shows up: Dynamic analytics scripts, search filters, and embedded configuration variables where backslash characters are not properly escaped/sanitized prior to string escaping.
- Quick detection: Pass test sequences containing backslashes and single quotes (`\';`) to verify if the server fails to double-escape backslashes (`\` -> `\\`), allowing backslash neutralization.
- Impact: Reflected XSS execution within victim sessions, allowing full JavaScript execution despite WAF and string escaping filters.
- In the report: Document the inline script reflection context, show the missing backslash escaping flaw, demonstrate the backslash neutralization breakout, and supply the reproduction URL.

## 8. Bypass / variants noticed

- Supplying multiple backslashes (e.g., `\\\'`) to test how the server handles nested or repetitive escaping logic.
- Using arithmetic operators instead of semicolons (e.g., `\'-alert(1)//`) to execute code within a single concatenated expression.

## 9. Takeaway

Flawed escaping implementations (such as blindly prepending `\` to `'` without escaping existing backslashes first) are vulnerable to backslash neutralization. Backend applications should rely on standard JSON serialization (e.g., `JSON.stringify()`) or safe HTML-encoded data attributes to pass backend data to client scripts securely.
