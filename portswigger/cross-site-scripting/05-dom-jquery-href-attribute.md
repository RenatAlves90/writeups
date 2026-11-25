# LAB: DOM XSS in jQuery anchor href attribute sink using location.search source

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-23                                                                                                                     |
| **Time**                    |                   5                                                                                                              |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-jquery-href-attribute-sink](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-href-attribute-sink) |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack on a submit feedback feature by identifying a client-side flow where user input from `location.search` is assigned to a jQuery `href` attribute sink, executing `alert(document.cookie)`.

## 2. Surface

- URL query parameters (`/feedback?returnPath=...`).
- Client-side jQuery script executing on the feedback submission page.
- DOM Sink: jQuery `attr('href', ...)` assignment updating a dynamic back/return link element.

## 3. Hypothesis

If client-side JavaScript extracts the `returnPath` parameter from `location.search` without URL validation or sanitization and assigns it directly to an anchor element's `href` attribute via jQuery's `attr()` method, injecting a `javascript:` pseudo-protocol URL will cause arbitrary JavaScript to execute when the link is clicked or triggered.

## 4. Payload that worked

Request:
```http
GET /feedback?returnPath=javascript:alert(document.domain) HTTP/2
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
Content-Length: 4291
<div class="is-linkback">
  <a id="backLink" href="javascript:alert(document.domain)">Back</a>
</div>
```
## 5. Why it works

Analyzing the client-side JavaScript execution on the `/feedback` page revealed how the back link destination was handled:

```javascript
$(function() { 
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath')); 
});
```

The jQuery script extracts the `returnPath` parameter directly from `window.location.search` using `URLSearchParams` and assigns its raw string value directly to the `href` attribute of the element with ID `backLink` via jQuery's `.attr()` method.

Because the application fails to validate the URL scheme or enforce relative paths, supplying `returnPath=javascript:alert(document.cookie)` populates the link with a `javascript:` pseudo-protocol URL (`<a id="backLink" href="javascript:alert(document.cookie)">`). When the user clicks the "Back" link, the browser executes the inline JavaScript context instead of navigating to a new HTTP resource, executing `alert(document.cookie)` within the session domain.

## 6. What I tried that failed

- Navigating directly to the `/feedback` page confirmed the presence of the dynamic return link element (`#backLink`).
- Inspecting the DOM and source code confirmed that the `returnPath` parameter value was assigned directly without URL parsing or sanitization.
- Testing standard HTML tags/payloads failed to execute automatically upon page load because `.attr('href', ...)` sets an attribute value rather than rendering executable markup in an HTML sink.
- Rule extracted: When user input flows into URL attributes (`href`, `src`, `action`), check if the action requires user interaction (such as clicking an `<a>` tag) and leverage pseudo-protocols (`javascript:`, `data:`) rather than standard HTML breakout tags.
  
## 7. In a real target (bounty translation)

- Where it shows up: Dynamic back buttons, return/redirect links on login or feedback pages, and single-page applications handling internal navigation parameters via client-side routing.
- Quick detection: Search front-end scripts for jQuery `attr('href', ...)` or standard DOM `.setAttribute('href', ...)` calls processing inputs from `location.search` or `location.hash`.
- Impact: Execution of arbitrary JavaScript in the victim's session context upon clicking the crafted link, leading to potential DOM tampering, session hijacking, or sensitive data extraction.
- In the report: Detail the client-side JavaScript flow from `location.search` to the `$().attr('href')` sink, explain the lack of scheme validation (allowing `javascript:` pseudo-protocol execution), and provide the PoC link.

## 8. Bypass / variants noticed

- Leveraging obfuscation within the pseudo-protocol string, such as URL encoding or HTML entity encoding (e.g., `javascript:alert%28document.cookie%29`), depending on how the browser normalizes attribute values.
- Utilizing `javascript:` payloads containing DOM manipulation, keylogging, or session-hijacking scripts triggered upon user interaction with the return button.
  
## 9. Takeaway

When dynamically setting destination URLs for links using user-controlled input, applications must strictly validate that the URL uses safe schemes (e.g., `http:` or `https:`) or use relative path parsing to prevent execution via the `javascript:` pseudo-protocol.
