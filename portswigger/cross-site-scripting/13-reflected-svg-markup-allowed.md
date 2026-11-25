# LAB: Reflected XSS with some SVG markup allowed

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-25                                                                                                                     |
| **Time**                    |                   15                                                                                                            |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-some-svg-markup-allowed](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-some-svg-markup-allowed) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature protected by a Web Application Firewall (WAF) that blocks most HTML tags and attributes, but permits a specific subset of SVG tags and animation elements to execute `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side Web Application Firewall (WAF) filtering incoming HTML/SVG tags, attributes, and event handlers.
- HTML reflection context: User input reflected directly into the page response body.

## 3. Hypothesis

If the WAF blocks standard HTML tags and event handlers but allows specific SVG structural and animation tags (such as `<svg>`, `<animatetransform>`, `<title>`, etc.), nesting an allowed animation tag containing an `onbegin` or `onend` event handler inside an allowed SVG container element will bypass the filter and execute JavaScript upon animation initialization.

## 4. Payload that worked

Request:
```http
GET /?search=%3Csvg+width%3D%2230%22+height%3D%2210%22%3E+++%3Ccircle+cx%3D%222%22+cy%3D%225%22+r%3D%221%22+fill%3D%22red%22%3E++++++++%3CanimateTransform+++++++++++++onbegin%3D%22alert%281%29%22++++++%2F%3E+++%3C%2Fcircle%3E+%3C%2Fsvg%3E HTTP/1.1
Host: <host>.h1-web-security-academy.net
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
Referer: https://<host>.h1-web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
Connection: keep-alive
```
Response:
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Connection: close
Content-Length: 6566
<h1>0 search results for '
  <svg width="30" height="10">
    <circle cx="2" cy="5" r="1" fill="red">
    <animateTransform onbegin="alert(1)" />
    </circle>
  </svg>'
</h1>
```
## 5. Why it works

Auditing the Web Application Firewall (WAF) using automated SVG tag and attribute fuzzing revealed that standard HTML tags and standard SVG animation tags (`<animate>`) were strictly blocked. However, the WAF ruleset omitted `<animateTransform>` from its tag blocklist and permitted the `onbegin` event handler.

Injecting `<animateTransform>` inside an allowed parent SVG element (such as `<circle>` within an `<svg>` root container) enables client-side JavaScript execution:
1. `<animateTransform>` is valid SVG markup designed to animate transform attributes (like scale or rotation) on graphics elements.
2. The `onbegin` event attribute is an animation-specific event handler that fires automatically as soon as the SVG element is initialized and rendered in the DOM.
3. Placing `onbegin="alert(1)"` inside `<animateTransform>` bypasses standard `on*` event filters on base elements (like `onload` or `onerror` on `<img>`/`<body>`) and triggers the JavaScript execution context immediately upon DOM insertion without requiring user interaction.

## 6. What I tried that failed

- Fuzzing standard HTML tags (`<script>`, `<img>`, `<iframe>`, `<body>`) returned HTTP 400/403 responses due to WAF blocklists.
- Testing standard SVG animation tags such as `<animate>` failed because `<animate>` was explicitly caught and blocked by the perimeter filter.
- Inserting a test payload with `onbegin="console.log(1)"` confirmed that the `onbegin` handler was permitted by the WAF and executed automatically during SVG rendering.
- Replacing `console.log` with `alert(1)` successfully executed the required PoC.
- Rule extracted: When perimeter WAFs block primary animation vectors (`<animate>`), alternative SVG animation tags like `<animateTransform>` or `<animateMotion>` can provide unblocked DOM insertion points, and animation initialization event handlers (`onbegin`, `onend`, `onrepeat`) can bypass standard DOM event filters.
  
## 7. In a real target (bounty translation)

- Where it shows up: Reflected search endpoints and dynamic input fields protected by legacy WAF rule-sets that permit SVG elements for graphics rendering while failing to account for SVG animation event handlers.
- Quick detection: Fuzzing SVG-specific tags (`<svg>`, `<animatetransform>`, `<animate>`, `<set>`) and animation event handlers (`onbegin`, `onend`, `onrepeat`) against the target parameter using Burp Intruder.
- Impact: Reflected XSS execution bypassing perimeter defenses, enabling session hijacking, client-side DOM manipulation, or malicious redirection.
- In the report: Detail the specific SVG tags permitted by the WAF whitelist, demonstrate the animation initialization event vector (`onbegin`), and provide the complete reproduction steps.

## 8. Bypass / variants noticed

- Leveraging alternative SVG animation event handlers if `onbegin` is filtered, such as `onend` or `onrepeat` (combined with short animation durations).
- Using alternative animation vector tags such as `<animateMotion>` or `<set>` paired with `onbegin` to trigger client-side execution.

## 9. Takeaway

Allowing subsets of SVG tags without strictly filtering SVG animation event handlers (such as `onbegin`, `onend`, or `onrepeat`) leaves applications vulnerable to XSS. Defense-in-depth requires proper contextual output encoding and restrictive Content Security Policies (CSP).
