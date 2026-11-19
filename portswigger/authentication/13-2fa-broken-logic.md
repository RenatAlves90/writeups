# LAB: 2FA simple bypass

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Multi-factor authentication)                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-18                                                                                                                   |
| **Time**                    |                                     2                                                                                           |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-2fa-simple-bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)              |

## 1. Objective

Bypass the two-factor authentication (2FA) check to access the account page of the target user (`carlos`) using known credentials (`carlos:montoya`).

## 2. Surface

- Primary authentication page (`/login`) validating first-stage credentials.
- Secondary authentication page (`/login2`) prompting for the 2FA verification code.
- User account page (`/my-account`) intended to be accessible only after full authentication.
- Session cookie state management during the multi-stage authentication flow.

## 3. Hypothesis

If the application sets a valid session cookie upon completing the first stage of authentication (`/login`) and relies strictly on client-side UI navigation to force the user to `/login2` without enforcing server-side access controls on `/my-account`, an attacker can bypass 2FA by directly navigating to the protected endpoint after submitting the first-stage credentials.

## 4. Payload that worked

Request (Stage 1 - First-factor authentication):
POST /login HTTP/1.1
Host: [lab-id].web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 33

username=carlos&password=montoya

Response:
```http
POST /login HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 30
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
Referer: https://<host>.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=carlos&password=montoya
```

Request


## 5. Why it works

The application generates and assigns a fully privileged session cookie immediately upon validating the first-factor credentials (`carlos:montoya`) at `/login`, prior to 2FA verification. The second-factor prompt (`/login2`) is enforced purely via client-side redirection. Navigating back to the home page or directly requesting authenticated endpoints like `/my-account` leverages the active, fully privileged session cookie, completely skipping the 2FA verification step.
## 6. What I tried that failed

- N/A — Direct navigation after Stage 1 authentication succeeded on the initial attempt due to the complete lack of server-side session scoping for unverified 2FA states.
- Rule extracted: When testing 2FA implementations, always evaluate whether the session cookie issued post-Stage 1 grants access to protected routes (`/`, `/my-account`, `/dashboard`) before the 2FA code is submitted.
  
## 7. In a real target (bounty translation)

- Where it shows up: Multi-stage authentication flows where the backend creates a fully privileged session upon credential check (Stage 1) instead of an restricted/pre-auth session token that only permits access to the 2FA endpoint.
- Quick detection: Log in with Stage 1 credentials, stop at the 2FA prompt, and attempt to manually browse to authenticated internal endpoints (e.g., `/dashboard`, `/my-account`, `/api/v1/user`).
- Impact: Complete 2FA bypass; renders multi-factor authentication entirely ineffective if an attacker obtains first-factor credentials.
- In the report: Provide request logs showing first-factor POST response setting a valid session cookie followed by direct access to `/my-account` without sending the `/login2` POST request.

## 8. Bypass / variants noticed

- Navigating to `/` (home page) post-Stage 1 and clicking the "My account" / "Login" link to trigger automatic redirection into the authenticated session.
- Direct URL manipulation by replacing `/login2` with protected application endpoints in the address bar or proxy history.
  
## 9. Takeaway

Authentication state must be strictly enforced on the server side. Session cookies issued during first-factor authentication should carry an explicit pre-authenticated scope limited strictly to 2FA verification endpoints until the second factor is fully validated.
