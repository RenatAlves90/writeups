# LAB: User ID controlled by request parameter with data leakage in response

|                             |                                                                                                                                                                                                            |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access control (IDOR + information disclosure)                                                                                                                                                             |
| **Difficulty**              | Apprentice                                                                                                                                                                                                 |
| **Date**                    | 2026-11-13                                                                                                                                                                                                 |
| **Time**                    | 6                                                                                                                                                                                                          |
| **Solved without solution** | yes                                                                                                                                                                                                        |
| **Link**                    | [lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect) |

## 1. Objective

This lab contains an access control vulnerability where sensitive information is leaked in the body of a redirect response.

To solve the lab, obtain the API key for the user carlos and submit it as the solution.

You can log in to your own account using the following credentials: wiener:peter

## 2. Surface

`/my-account?id=<GUID>` — direct swapping is blocked, but the app has a password
reset flow and the _responses_ may carry more than the UI shows.

## 3. Hypothesis

If a response contains more data than the UI renders (redirect targets, hidden
fields, response bodies of pre-auth endpoints), the other user's identifier or
credential may leak there.

## 4. Payload that worked

Request

```http
GET /my-account?id=carlos HTTP/2
Host: 0ad800e303ad29c381bc390c00330090.web-security-academy.net
Cookie: session=sjKNAB69LANw6kWASUPS5atiTZPgvyCF
Cache-Control: max-age=0
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
Referer: https://0ad800e303ad29c381bc390c00330090.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response

```
<p>Your username is: carlos</p>
<div>Your API Key is: kY1VIJKWqpJdQQGeMNB27zwoomdg0r1A</div>
```

## 5. Why it works

The server validates the request and builds the account object for the requested
`id`, but then issues a **redirect** whose body still contains the user's data
(the API key included). The browser discards that body and follows the `Location`
header, so the leak is invisible in normal usage — it only exists in the raw
response.

Root cause is the same as lab 05: the `id` parameter is trusted as the identity.
The additional lesson is about **observation surface**: an authorization check
can be correct on the endpoint the UI uses while sensitive data is still
over-returned on a response nobody renders. `302` responses, headers and error
bodies are part of the attack surface.

## 6. What I tried that failed

No failed payloads. What worked was the observation method, not a clever swap:

- I read the response in the **Repeater** with redirects not followed, so the
  raw body of the redirect was visible — the API key was there.
- The realization: a browser following the `Location` header would have
  discarded this body entirely. The leak is invisible in normal usage; it exists
  only in the raw response.

Rule extracted: rendered page and raw response are two different observation
surfaces. Authentication checks can be correct on the endpoint the UI uses while
sensitive data is still over-returned in a response nobody renders.

## 7. In a real target (bounty translation)

- Always read the **raw** response in Repeater, never the rendered page.
- Sensitive data leaks in: redirects (Location header), HTML comments, hidden
  inputs, JSON fields the front-end ignores, error messages, response headers.
- Chain idea for bounty: reset flow + leaked identifier + second endpoint = full
  account takeover. Chained IDOR reports pay more than single ones.
- Impact: ATO via leaked credential/identifier → Critical.
- In the report: raw request + raw response with the leaked field highlighted.

## 8. Bypass / variants noticed

- Repeat with "Follow redirects" both on and off; the leak only appears in the
  raw 3xx body.
- Check other over-returning surfaces: HTML comments, hidden input values,
  fields the front-end ignores (e.g. `password`, `roleid`, `isAdmin`),
  verbose error pages, `X-*` debug headers.
- Chain potential for bounty: leaked credential/identifier + second endpoint
  (login, API) = account takeover. Chained reports pay more than single ones.

## 9. Takeaway

The rendered page lies; the raw response tells the truth. Read every 3xx body
in the Repeater before following the redirect — leaks live exactly there.
