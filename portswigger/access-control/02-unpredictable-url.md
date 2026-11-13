# LAB: Unprotected admin functionality with unpredictable URL

|                             |                                                                                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access Control                                                                                                                                                               |
| **Difficulty**              | Apprentice                                                                                                                                                                   |
| **Date**                    | 2026-11-11                                                                                                                                                                   |
| **Time**                    | 4                                                                                                                                                                            |
| **Solved without solution** | yes                                                                                                                                                                          |
| **Link**                    | [lab-unprotected-admin-functionality-with-unpredictable-url](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality-with-unpredictable-url) |

## 1. Objective

Discover the admin panel's URL (which uses a randomized path) and delete `carlos`.

## 2. Surface

A random path (`/admin-<hash>`) **embedded in the JavaScript** loaded by the
homepage. Not in robots.txt-it lives in the code delivered to the client.

## 3. Hypothesis

If the path is unpredictable but the front-end needs to know it to build the
panel link, then the path is inside the HTML/JS I receive. Hiding it on the
client is not access control.

## 4. Payload that worked

In Burp's **HTTP history**, I located the request for the script loaded by the
homepage (`/resources/js/...`), opened the response and found:

```javascript
var isAdmin = false;
if (isAdmin) {
    var adminPanelTag = document.createElement('a');
    adminPanelTag.setAttribute('href', '/admin-123b');
    ...
}
```

```
GET /admin-123b HTTP/1.1
Host: xxxx.web-security-academy.net
### Panel opened → GET /admin-<random>/delete?username=carlos → solved.
```

## 5. Why it works

A random path is obscurity, not authorization. The script that builds the link is delivered to every visitor; anyone can read the path. And the endpoint checks no role.

## 6. What I tried that failed

## 7. In a real target (bounty translation)

Where it shows up: SaaS apps with SPAs-"secret" routes in bundled JS (path:, /admin, /internal, /console, /manage).
Quick detection: download every .js from urls_js.txt and run grep -Ei 'admin|internal|manage|console|dashboard'.
Impact: same as lab 01 → High/Critical.
In the report: cite the JS file and the line containing the route, plus the access request. Proof the route was publicly discoverable.

## 8. Bypass / variants noticed

Source maps (.js.map) reveal even more routes and component names.
Check data-\* attributes and HTML comments as alternatives to the JS.

## 9. Takeaway

Any secret delivered to the browser is not a secret. If the UI needs to know it, the attacker knows it too-always read the target's JavaScript.
