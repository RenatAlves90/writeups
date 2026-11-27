# LAB: Reflected XSS into a JavaScript template literal with angle brackets, single, double quotes, backslash and backticks escaped

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |        5                                                                                                                  |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where input is reflected inside a JavaScript template literal, and special characters (`<`, `>`, `'`, `"`, `\`, `` ` ``) are escaped or encoded, executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side encoding and escaping filters targeting angle brackets, single/double quotes, backslashes, and backticks.
- Inline JavaScript template literal reflection context: Input reflected directly inside backticks (e.g., ``var searchTerms = `USER_INPUT`;``).

## 3. Hypothesis

If user input is reflected inside an ES6 template literal (enclosed in backticks `` ` ``) and the application escapes quote delimiters and backticks, an attacker does not need to break out of the string boundary. Template literals support native string interpolation via the `${...}` syntax. Since the JavaScript parser evaluates expressions inside `${}` prior to string construction, arbitrary code can be executed directly inside the template expression without breaking out of the surrounding string.

## 4. Payload that worked

Request:
```http
curl --url ^"https://<host>.web-security-academy.net/?search=^%^24^%^7Balert^%^28document.domain^%^29^%^7D^" ^
  -H ^"accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7^" ^
  -H ^"accept-language: en-US,en;q=0.9^" ^
  -H ^"cache-control: no-cache^" ^
  -b ^"session=sess^" ^
  -H ^"pragma: no-cache^" ^
  -H ^"priority: u=0, i^" ^
  -H ^"referer: https://<host>.web-security-academy.net/?search=^%^5C^%^60+^%^26grave^%^3B^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"158^\^", ^\^"Not.A/Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"158^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-fetch-dest: document^" ^
  -H ^"sec-fetch-mode: navigate^" ^
  -H ^"sec-fetch-site: same-origin^" ^
  -H ^"sec-fetch-user: ?1^" ^
  -H ^"upgrade-insecure-requests: 1^" ^
```
Response:
```http
HTTP/2 302 Found
Location: /post/comment/confirmation?postId=3
X-Frame-Options: SAMEORIGIN
Content-Length: 0

<script>
  var message = `0 search results for '${alert(document.domain)}'`;
  document.getElementById('searchMessage').innerText = message;
</script>
```
## 5. Why it works

Analyzing the inline script block revealed that user input is reflected directly inside an ES6 JavaScript template literal (enclosed by backticks `` ` ``):

```html
<script>
    var message = `0 search results for 'USER_INPUT'`;
    document.getElementById('searchMessage').innerText = message;
</script>
```

The application attempts to prevent breakout attacks by escaping angle brackets, quotes, backslashes, and backticks (converting backticks into Unicode escape sequences like `\u0060`).

However, the application fails to sanitize or escape the ES6 template literal expression interpolation syntax (`${...}`):
1. JavaScript template literals automatically evaluate any valid expression enclosed within `${...}` before returning the final string value.
2. Injecting `${alert(1)}` forces the JavaScript engine to evaluate the `alert(1)` call during template string construction.
3. Because code execution occurs natively *inside* the interpolation boundary, the payload does not require breaking out of the backtick string literal, bypassing backtick and backslash escaping filters entirely.

## 6. What I tried that failed

- Submitting backticks (`` ` ``) and backslash-escaped backticks (`` \` ``) failed because the backend transformed backticks into Unicode escape sequences (`\u0060`), keeping the string boundary intact.
- Fuzzing curly braces (`{}`) confirmed that standard object syntax and single characters were reflected without sanitization.
- Injecting `${alert(1)}` immediately triggered JavaScript expression evaluation within the template literal context.
- Rule extracted: When user input is reflected inside JavaScript template literals (backtick strings), attempting to break out of quotes or backticks is unnecessary. If `${}` interpolation delimiters are unescaped, arbitrary JavaScript code can be executed directly within the expression block.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic frontend rendering engines, modern JavaScript single-page applications (SPAs), and inline script blocks using template strings for string formatting.
- Quick detection: Submit `${1+1}` into parameters reflected inside JavaScript blocks. Inspect the DOM to verify if the output resolves to `2` inside the template string.
- Impact: Reflected XSS execution bypassing typical quote and backslash filters.
- In the report: Document the template literal context, highlight the lack of `${}` expression filtering, and demonstrate the expression interpolation PoC.

## 8. Bypass / variants noticed 

- Executing complex expressions or function calls inside interpolation blocks: `${alert(document.domain)}` or `${window.onerror=alert,throw 1337}`.
- Chaining multiple statements inside an IIFE (Immediately Invoked Function Expression) within the interpolation boundary: `${(()=>alert(1))()}`.

## 9. Takeaway

Escaping quotes, backslashes, and backticks is insufficient when reflecting input into JavaScript ES6 template literals. Applications must sanitize or strip the `${}` interpolation syntax or use traditional string escaping and standard data binding models.
