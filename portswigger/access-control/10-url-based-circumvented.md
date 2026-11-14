# LAB: URL-based access control can be circumvented

| | |
|---|---|
| **Topic** | Access control (URL-based ACL bypass) |
| **Difficulty** | Practitioner |
| **Date** | 2026-11-14 |
| **Time** | <min> |
| **Solved without solution** | <yes/no> |
| **Link** | portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented |

## 1. Objective
Reach `/admin` and delete `carlos` as a regular user, when `/admin` is blocked
by an access control layer in front of the application.

## 2. Surface
Two layers: a front-end control that decides on the **request URL**, and a
back-end that resolves the route from its own logic. Any mismatch between what
the front-end sees and what the back-end routes is a bypass.

## 3. Hypothesis
If the back-end is a framework/proxy stack that honors rewrite headers, sending
a benign-looking URL with `X-Original-URL`/`X-Rewrite-URL` makes the front-end
authorize "/" while the back-end routes to `/admin`.

## 4. Payload that worked
```http
GET /?username=carlos HTTP/2
Host: host.web-security-academy.net
Cookie: session=session
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
Referer: https://host.web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
X-Original-Url: /admin/delete
```
```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works
The front-end security layer (such as a reverse proxy or WAF) evaluates authorization based solely on the path in the request line (/), which is fully accessible to regular users. However, the origin server (back-end) supports pseudo-headers like X-Original-URL for internal routing and URL rewriting. By supplying X-Original-Url: /admin/delete, the front-end authorizes the request because the request line appears benign, while the backend honors the override header and routes the execution to the restricted administrative handler. Furthermore, required parameters like username=carlos must be supplied correctly as part of the query string to satisfy the backend route requirements.

## 6. What I tried that failed
Direct requests to /admin or /admin/delete, which were blocked by the front-end access control layer.

Submitting the routing override header initially without including the required action parameters, leading to "missing parameter" errors until realizing the parameters needed to be included in the request URL.

## 7. In a real target (bounty translation)
- This is the standard play behind CDNs/WAFs (Cloudflare, AWS WAF, nginx ACLs).
- Quick test set: `X-Original-URL: /admin`, `X-Rewrite-URL: /admin`, then
  normalization variants (`//admin`, `/./admin`, `/;/admin`, `/Admin`,
  `/%2f/admin`).
- If a WAF blocks the *path* but the origin routes differently, you get 200
  from an endpoint that "doesn't exist" for you — always verify the response
  body, not the status alone.
- Impact: depends on what the bypass unlocks — usually High.

## 8. Bypass / variants noticed
Using alternative header variations such as X-Rewrite-URL or X-Forwarded-Url.

Proxy normalization bypasses such as path traversal segments (/./admin), double slashes (//admin), or semicolon modifiers (/;/admin).

## 9. Takeaway
When access control lives in a proxy, ask what the origin server would do with
the same request. The mismatch between front-door and back-door is the bug.
