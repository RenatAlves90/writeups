# LAB: User role controlled by request parameter

|                             |                                                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access control (vertical privilege escalation)                                                                                                     |
| **Difficulty**              | Apprentice                                                                                                                                         |
| **Date**                    | 2026-11-12                                                                                                                                         |
| **Time**                    | 9                                                                                                                                                  |
| **Solved without solution** | yes                                                                                                                                                |
| **Link**                    | [lab-user-role-controlled-by-request-parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter) |

## 1. Objective

Escalate from regular user to administrator and delete `carlos`.

## 2. Surface

**Cookie** `Admin=false`, set by the server at login. The user's role is derived
directly from that client-controllable value.

## 3. Hypothesis

If the server decides the role by reading a cookie instead of a database record
bound to the session, then tampering with the cookie makes me an admin.

## 4. Payload that worked

```http
GET /admin HTTP/1.1
Host: xxxx.web-security-academy.net
Cookie: session=<session>; Admin=true
```

Panel with the delete link → GET /admin/delete?username=carlos with the same cookie → solved.

## 5. Why it works

The server reads Admin from the request instead of querying the authenticated user's role from the session. Authentication exists; authorization is outsourced to the client.

## 6. What I tried that failed

I wasted time testing query parameters (?admin=true, ?role=admin) without having looked at the request headers. The role wasn't in the URL-it was in the cookie.

Lesson: the privilege-injection surface is not just the URL. A request has four places-path, query, body, and headers/cookies-and I had only looked at one. Next time: open the entire raw request in HTTP history before forming any payload.

## 7. In a real target

Where it shows up: legacy apps with "preference" cookies carrying authorization state (role=, isAdmin, type=, plan=).
Quick detection: read all cookies in the request (including the ones the UI never mentions) and try alternative values (true, 1, admin, 2).
Also check: JWT "role" claim, custom headers (X-Role, X-Admin), and the JSON body where applicable.
Impact: full vertical escalation → High/Critical, one of the easiest findings for a triager to accept.
In the report: two requests side by side (Admin=false and Admin=true) plus a screenshot of the panel. Use Comparer to highlight the difference.

## 8. Bypass / variants noticed

Casing: TRUE, True.
Signing: if the cookie is signed (e.g. Admin=false; hash=), changing the value breaks the signature-but sometimes the server never validates the hash.
If the cookie doesn't work, try the same value in query/body/headers.

## 9. Takeaway

Before crafting any payload, read the whole request: path, query, body, headers, cookies. Half of beginner IDORs are lost to an unread cookie.
