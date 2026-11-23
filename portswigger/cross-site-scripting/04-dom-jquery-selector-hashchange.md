# LAB: DOM XSS in jQuery selector sink using a hashchange event

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-23                                                                                                                     |
| **Time**                    |            25                                                                                                                     |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-jquery-selector-hash-change-event](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-selector-hash-change-event) |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack on a blog application by exploiting a jQuery selector sink connected to a `hashchange` event listener, ultimately delivering an exploit via the Exploit Server to execute `print()` on the victim's browser.

## 2. Surface

- URL fragment/hash (`location.hash`).
- Client-side jQuery script handling page scrolling/navigation on `window.onhashchange`.
- DOM Sink: Vulnerable jQuery selector `$()` consuming `location.hash`.

## 3. Hypothesis

If a client-side script passes the un-sanitized `location.hash` directly into jQuery's `$()` selector function inside a `hashchange` event listener, an attacker can craft a payload containing HTML elements (such as `<img src=x onerror=...>`). Older/vulnerable versions of jQuery will parse the injected string as HTML and instantiate the element, executing the embedded JavaScript payload when the fragment changes.

## 4. Payload that worked

Request:
```http
GET /exploit HTTP/2
Host: exploit-<host>.exploit-server.net
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Referer: https://exploit-<host>.exploit-server.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
Server: Academy Exploit Server
Content-Length: 142

<iframe src="https://<host>.web-security-academy.net/#" onload="this.src+='<img src=x onerror=print()>'"></iframe>
```
## 5. Why it works

Analyzing the client-side JavaScript handling the `hashchange` event listener revealed the target code execution path:

```javascript
$(window).on('hashchange', function(){
    var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
    if (post) post.get(0).scrollIntoView();
});
```

The script listens for changes to `window.location.hash`, extracts the fragment string skipping the initial `#` symbol (`window.location.hash.slice(1)`), decodes it via `decodeURIComponent`, and concatenates it directly into a jQuery selector string passed to `$()`.  In vulnerable jQuery versions, the `$()` selector function double-purposes as both a DOM element query selector and an HTML element creator. When a string containing HTML tags (such as `<img src=x onerror=print()>`) is passed into `$()`, jQuery parses the string as raw HTML markup rather than a pure CSS/text selector. Instantiating the dynamic `<img>` tag in memory immediately triggers the `onerror` event handler when the invalid image source `x` fails to load, executing `print()`.

To trigger this headlessly against a victim without requiring manual hash navigation, an attacker delivers an `<iframe>` hosted on an exploit server. The `<iframe>` initial `src` loads the vulnerable application endpoint with an empty fragment (`#`). Upon triggering the `onload` event, the frame's `src` is appended with the malicious HTML payload string, raising a `hashchange` event inside the victim frame context and executing the payload automatically.

## 6. What I tried that failed

- Manually exploring `document.location.hash = "valor"` in the browser Developer Console confirmed that updating the fragment dynamically fired the `window.onhashchange` event handler as expected.
- Injecting standard text parameters failed to alter DOM behavior until raw HTML tags were introduced directly into the hash fragment.
- Testing direct page loads with the payload inside the URL hash initially required an explicit fragment change event (`hashchange`) to fire the listener callback; embedding the action inside an `<iframe>` with an `onload` handler successfully forced the event to trigger automatically.
- Rule extracted: When exploiting `hashchange` event listeners, manual URL navigation might not always trigger the event on initial load. Using an `<iframe>` to load the base URL first and subsequently update `src` or `location.hash` programmatically ensures the `hashchange` handler executes predictably.  

## 7. In a real target (bounty translation)

- Where it shows up: Legacy web applications using older jQuery versions (e.g., pre-1.9/3.0) that implement auto-scrolling, tab switching, or smooth anchor link navigation via `$(location.hash)`.
- Quick detection: Search front-end scripts for `$(location.hash)`, `$(window.location.hash)`, or `$(hash)` within `hashchange` or `DOMContentLoaded` event handlers.
- Impact: Unauthenticated remote code execution on the client-side via a specially crafted link or an iframe on an attacker-controlled site, allowing session hijacking, DOM manipulation, or forced actions.
- In the report: Identify the exact version of jQuery, point out the unsafe `$()` call consuming `location.hash`, document the `hashchange` trigger mechanism, and provide an iframe-based exploit PoC.

## 8. Bypass / variants noticed

- Delivering payloads via nested `<iframe>` tags or `window.open()` cross-origin popups that programmatically change the target window's `location.hash` after initial load.
- Utilizing alternate HTML vector tags (`<svg onload=...>`, `<iframe onload=...>`) compatible with legacy jQuery selector parsing routines.
  
## 9. Takeaway

Do not pass untrusted user input or URL fragments directly into the jQuery `$()` selector function without prior validation or explicit sanitization. Use `$(document.getElementById(...))` or specific string parsing/sanitization to ensure input is treated strictly as an element ID or selector, rather than executable HTML markup.
