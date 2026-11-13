# LAB: Unprotected admin functionality

|                             |                                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Access Control                                                                                                                 |
| **Difficulty**              | Apprentice                                                                                                                     |
| **Date**                    | 2026-11-11                                                                                                                     |
| **Time**                    | 5                                                                                                                              |
| **Solved without solution** | yes                                                                                                                            |
| **Link**                    | [lab-unprotected-admin-functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality) |

## 1. Objective

Access the administrative panel without authentication and delete the user `carlos`.

## 2. Surface

A direct server path: `/admin`, with no session or role check whatsoever.
Discovered via **passive enumeration**-`robots.txt` listed `Disallow: /admin`.

## 3. Hypothesis

If the panel exists at a predictable path and the server performs no authorization
check, any unauthenticated visitor can open it.

## 4. Payload that worked

Request:

```http
GET /admin HTTP/1.1
Host: xxx.web-security-academy.net
```

Response:

```
panel listing users, with a "Delete" link next to `carlos`.
`GET /admin/delete?username=carlos` → lab solved.
```

## 5. Why it works

Authorization is enforced **only in the front-end** (the panel link is not shown
to regular users), but the endpoint itself validates neither role nor session.
The server trusts that nobody will type the URL.

## 6. What I tried that failed

## 7. In a real target (bounty translation)

- Where it shows up: home routers, CMS panels, Jenkins/Grafana/Kibana, internal
  tools forgotten on subdomains.
- Quick detection: `robots.txt`, `sitemap.xml`, HTML comments, path dictionary
  (`ffuf` with a small wordlist: admin, administrator, panel, manage, console, internal).
- Impact: full administrative access with no authentication → High/Critical.
- In the report: exact path + screenshot of the panel + a request that performs
  an admin action (delete/create), not just the page loading.

## 8. Bypass / variants noticed

- Check whether `X-Forwarded-For: 127.0.0.1` unlocks the panel (IP-based filter).
- Try `/admin` with and without trailing slash, different casing, `%2f`.

## 9. Takeaway

If the link isn't in the UI, the endpoint may still exist. Always enumerate
paths and read robots.txt/sitemap before hunting for a "hard" vulnerability.
