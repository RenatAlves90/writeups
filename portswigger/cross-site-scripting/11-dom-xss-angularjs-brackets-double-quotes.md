# LAB: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-23                                                                                                                     |
| **Time**                    |            20                                                                                                                     |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-angularjs-expression](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-angularjs-expression)       |

## 1. Objective

Perform a DOM-based Cross-Site Scripting (XSS) attack on an application using AngularJS by exploiting user input reflected inside an `ng-app` directive context to execute `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Client-side JavaScript framework: AngularJS rendered on the page.
- DOM Sink: AngularJS expression evaluator consuming client-side input within an `ng-app` container.

## 3. Hypothesis

If user input is reflected inside an HTML element managed by an AngularJS directive (such as `ng-app`), even if standard HTML characters like `<` and `>` are encoded, AngularJS will evaluate template expressions enclosed in double curly braces (`{{...}}`). Injecting AngularJS expression payloads will execute JavaScript directly within the framework's evaluation scope.

## 4. Payload that worked

Request:
```http
GET /?search=%7B%7Bconstructor.constructor%28%27alert%281%29%27%29%28%29%7D%7D HTTP/2
Host: <host>.web-security-academy.net
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
Referer: https://<host>.web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
Content-Length: 3460
```

## 5. Why it works

Analyzing the client-side page structure revealed that user input was reflected directly inside an element managed by an AngularJS directive (`ng-app`).

When input is rendered within an AngularJS template scope, the client-side framework automatically parses and evaluates expressions enclosed inside double curly braces (`{{...}}`). Evaluating `{{9*9}}` returned `81`, confirming that the application dynamically compiles user-controlled input as AngularJS template code without HTML-encoding or sanitizing expression syntax.

In AngularJS, standard JavaScript primitives like `alert()` cannot be called directly inside basic template expressions because the framework evaluates expressions within its own internal `$scope` context rather than the global `window` object. 

To execute arbitrary code, the payload leverages prototypal inheritance via `constructor.constructor`:
1. `constructor` accesses the constructor function of an AngularJS scope object or primitive (Function / Object).
2. The second `.constructor` accesses the global JavaScript `Function` constructor.
3. Invoking `Function('alert(1)')` dynamically generates an anonymous function containing the payload in the global scope.
4. The trailing `()` immediately executes the generated function, escaping the AngularJS sandbox/scope and executing `alert(1)` within the `window` context.

## 6. What I tried that failed

- Testing arithmetic expressions like `{{9*9}}` rendered `81`, confirming that the AngularJS expression parser was actively compiling raw input from the query string.
- Attempting standard inline function calls such as `{{alert(1)}}` failed because `alert` is not a valid method on the AngularJS `$scope` object context.
- Attempting basic reflective properties or standard JavaScript window properties failed due to the scope isolation maintained by the framework parser.
- Rule extracted: Using published framework payload techniques (such as `constructor.constructor('code')()`) is standard practice when dealing with client-side template injection (CSTI). When AngularJS evaluates raw input within an `ng-app` scope, escaping the local `$scope` via constructor references is the canonical approach to reach global `window` functions.

## 7. In a real target (bounty translation)

- Where it shows up: Front-end applications using legacy framework templates (AngularJS v1.x), server-rendered pages containing client-side framework directives, and search inputs rendered inside template scopes.
- Quick detection: Search front-end markup for attributes like `ng-app` or `ng-controller`. Test inputs with basic arithmetic expressions (e.g., `{{7*7}}`) to verify if the client-side framework evaluates expressions in the DOM.
- Impact: Execution of arbitrary client-side JavaScript despite traditional HTML-encoding defenses, leading to DOM manipulation, session hijacking, or unauthorized actions.
- In the report: Identify the exact AngularJS framework version, document the `ng-app` boundary, point out the unescaped template expression evaluation, and provide the reproduction link.

## 8. Bypass / variants noticed

- Accessing global scope via alternative property paths, such as `$eval.constructor('alert(1)')()` or `$on.constructor('alert(1)')()`.
- Utilizing framework-specific sandbox escapes depending on the exact AngularJS 1.x version deployed (e.g., using `toString.constructor` or `$element` object traversal).

## 9. Takeaway

HTML entity encoding is insufficient to prevent XSS when user input is reflected within client-side template framework scopes (like AngularJS). Applications must avoid reflecting raw user input inside directive-managed containers or enforce proper contextual escaping and Content Security Policies (CSP).
