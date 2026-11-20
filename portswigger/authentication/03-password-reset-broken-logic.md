# LAB: Password reset broken logic

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Other mechanisms)                                                                                             |
| **Difficulty**              | Apprentice                                                                                                                 |
| **Date**                    | 2026-11-20                                                                                                                   |
| **Time**                    |          5                                                                                                                       |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-password-reset-broken-logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic) |

## 1. Objective

Exploit broken logic in the password reset mechanism to change the password of the target user (`carlos`) and access their account page.

## 2. Surface

- Password reset request endpoint (`/forgot-password`).
- Password reset token submission / confirmation endpoint (`/forgot-password?temp-token=...`).
- Password reset HTTP POST handler.
- Target user account (`carlos`).

## 3. Hypothesis

If the password reset functionality relies on a hidden client-side input parameter (such as a `username` field) during the final POST request instead of strictly deriving the target identity from a verified, single-use server-side reset token, changing the target username parameter will reset the password of arbitrary users.

## 4. Payload that worked

Request:
```http
POST /forgot-password?temp-forgot-password-token=ggx1hy13feqfrrvs3huwwr5ka3u3ljod HTTP/2
Host: host.web-security-academy.net
Cookie: session=sess
Content-Length: 117
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://host.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://host.web-security-academy.net/forgot-password?temp-forgot-password-token=b8tcb1brlz167kdzr8e3ehaxnk3thg1o
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

temp-forgot-password-token=ggx1hy13feqfrrvs3huwwr5ka3u3ljod&username=carlos&new-password-1=peter&new-password-2=peter
```
Response:
```http
HTTP/2 200 OK
Content-Type: text/html; charset=utf-8
Set-Cookie: session=sess; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 8630
```

## 5. Why it works

The application suffers from broken logic in its password reset functionality because it fails to enforce server-side binding between the password reset token and the target user account. When the POST request to reset the password is submitted, the backend receives both the validation token and the `username` parameter. Rather than deriving the user context exclusively from the verified server-side token state, the backend uses the client-supplied `username` parameter to identify which account's password should be updated. Because the token is validated independently without verifying that it belongs to `carlos`, submitting a valid reset token (generated for `wiener`) along with `username=carlos` successfully overwrites the target user's password.
## 6. What I tried that failed

- Tested changing the `username` parameter during the initial POST request to `/forgot-password` (Stage 1), which failed to trigger a password reset for `carlos` because the email reset link was dispatched to the address associated with the provided user context without exposing a usable token directly.
- Attempted to submit the password reset POST request without supplying a `temp-token` parameter or using an arbitrary/malformed token, which resulted in immediate rejection by the application due to token validation failures.
- Rule extracted: When analyzing password reset forms that include both a reset token and explicit user identifiers (such as `username` or `email` parameters) in the final submission payload, test whether the user identity can be swapped while supplying any valid, server-accepted reset token.

## 7. In a real target (bounty translation)

- Where it shows up: Password reset flows that pass both a validation token and a explicit user identifier (e.g., `username`, `email`, `user_id`) in the final password submit request, but validate only token format rather than token-to-user binding.
- Quick detection: Request a legitimate password reset for your own account. Intercept the final POST request when submitting the new password. Identify if parameters like `username` or `email` are present in the POST body or query string, and change them to a target user (`carlos`).
- Impact: Unauthenticated full account takeover of any known target user.
- In the report: Document the complete HTTP POST request demonstrating the modification of the `username` parameter alongside a valid token, followed by successful login credentials verification.

## 8. Bypass / variants noticed

- Intercepting the final password reset POST request in Burp Suite and modifying parameters such as `username`, `email`, or `user_id` to target alternate accounts while using a legitimately obtained reset token.
- Testing for parameter pollution (e.g., supplying `username=wiener&username=carlos`) or body vs. query string parameter mismatches to evaluate how different application layers parse user identifiers during token validation.

## 9. Takeaway

Password reset confirmation requests must never rely on client-supplied user identifiers. The backend must strictly extract the target identity directly from the cryptographically validated, single-use reset token stored in the server-side state.
