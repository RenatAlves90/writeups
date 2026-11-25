# LAB: Reflected DOM XSS

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | PRACTITIONER                                                                                                                     |
| **Date**                    | 2026-11-23                                                                                                                     |
| **Time**                    |            34                                                                                                                     |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-dom-xss-reflected](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-reflected)             |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack on a search feature where the application processes a reflected JSON response client-side and evaluates user input via `eval()`, executing `alert(document.domain)`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Asynchronous HTTP request fetching JSON search results via dynamic script execution (`search-results?search=...`).
- DOM Sink: `eval(...)` call inside client-side JavaScript handling the JSON search response.

## 3. Hypothesis

If server-side responses return raw user input inside a JSON structure and client-side JavaScript passes the evaluated string directly into `eval()` without escaping or parsing via `JSON.parse()`, breaking out of the JSON string literal using quote delimiters (`"`) and string concatenation (`+`) will execute arbitrary JavaScript within the `eval()` sink scope.

## 4. Payload that worked

Request:
```http
GET /search-results?search=%5C%22-alert%28%29%7D%2F%2F HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://<host>.web-security-academy.net/?search=%5C%22-alert%28%29%7D%2F%2F
Accept-Encoding: gzip, deflate, br
```
Response:
```http
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 44

{"results":[],"searchTerm":"\\"-alert()}//"}
```
## 5. Why it works

Analyzing the client-side JavaScript responsible for fetching dynamic search results revealed an unsafe parsing pattern within the XMLHttpRequest handler:

```javascript
xhr.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        eval('var searchResultsObj = ' + this.responseText);
        displaySearchResults(searchResultsObj);
    }
};
```

Instead of using `JSON.parse()`, the application executes the raw HTTP response string directly inside an `eval()` sink to instantiate the JavaScript object `searchResultsObj`. 

When a search term is submitted, the server reflects the input inside a JSON response: `{"results":[],"searchTerm":"userInput"}`. Because `eval()` parses the response as executable JavaScript code, injecting `\"-alert(document.domain)}//` alters the execution path:
1. The leading escaped quote `\"` breaks out of the JSON string literal boundary inside the `eval()` execution context.
2. The hyphen `-` acts as a valid JavaScript arithmetic operator connecting the preceding string variable assignment.
3. `alert(document.domain)` is called as a valid JavaScript expression during the evaluation phase.
4. The closing brace `}` closes the surrounding JavaScript object block, and the line comment `//` instructs the JavaScript engine to ignore any remaining trailing JSON syntax that would otherwise cause a `SyntaxError`.

## 6. What I tried that failed

- Inspecting the initial page search behavior led to locating the XHR callback inside the client-side page source.
- Submitting standard HTML breaking characters like `"` and `'<>` reflected inside the JSON object but failed to trigger code execution directly.
- Attempting payloads like `"alert()` or `"-alert()` failed due to JavaScript syntax errors caused by unclosed quotes and unparsed trailing JSON characters inside the string processed by `eval()`.
- Rule extracted: When user input is reflected inside an `eval('var obj = ' + response)` sink, payload construction requires breaking out of the JavaScript string literal, maintaining valid JS expression syntax (e.g., using operators like `-`), and appending single-line comments (`//`) to suppress remaining trailing structural characters.

## 7. In a real target (bounty translation)

- Where it shows up: Legacy AJAX search handlers, single-page application dynamic data loaders, and legacy JSON response parsers relying on `eval()` instead of standard JSON parsers.
- Quick detection: Trace network responses returning JSON data and audit front-end JavaScript for direct `eval()` parsing of raw XHR or fetch responses containing reflected query inputs.
- Impact: Client-side code execution in the victim's session context upon viewing a malicious search URL, leading to session compromise, DOM manipulation, or credential exfiltration.
- In the report: Map the flow from the reflected API parameter to the dynamic JSON payload, point out the unsafe `eval()` sink call, document the string escaping breakout mechanism, and supply the reproduction link.

## 8. Bypass / variants noticed

- Using alternative JS operators or concatenation vectors inside the `eval()` payload, such as `\"+alert()+//` or `\";alert();//`.
- Replacing line comments (`//`) with block comments (`/* ... */`) if the target context strips forward slashes or handles multiline responses.

## 9. Takeaway

Applications must parse JSON using safe APIs such as `JSON.parse()` instead of executing string data dynamically with `eval()`. Server-side endpoints reflecting user parameters inside JSON structures must also apply contextual JSON string escaping.
