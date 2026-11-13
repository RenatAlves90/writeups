# Access Control

Labs, notes, and takeaways for access control vulnerabilities: vertical and
horizontal privilege escalation, IDOR, and mass assignment.

## Labs

### Apprentice
- [x] Unprotected admin functionality — [writeup](./01-unprotected-admin-functionality.md)
- [x] Unprotected admin functionality with unpredictable URL — [writeup](./02-unpredictable-url.md)
- [x] User role controlled by request parameter — [writeup](./03-user-role-controlled-by-request-parameter.md)
- [x] User role can be modified in user profile — [writeup](./04-user-role-can-be-modified-in-user-profile.md)
- [x] User ID controlled by request parameter — [writeup](./05-user-id-controlled.md)
- [x] Insecure direct object references — [writeup](./06-insecure-direct-object-references.md)
- [x] User ID controlled by request parameter, with unpredictable user IDs — [writeup](./07-unpredictable-user-ids.md)
- [x] User ID controlled by request parameter with data leakage in response — [writeup](./08-data-leakage-in-response.md)



## Takeaways

Access control always asks the same question: **where does the server get the
identity and the permission from?** If the answer is "from what the client sent"
(path, query, body, cookie, header, JWT claim), it is IDOR or privilege escalation.

Checklist before any payload:

1. Read the **entire** request — path, query, body, headers, cookies
2. Identify which field carries identity or role, and in which channel it lives
3. Test with **two accounts**
4. Compare responses side by side (Burp Comparer)

## Notes

- `Content-Type: application/json` means the body is the surface — query and
  cookies are usually noise for that endpoint.
- A response that returns a field (e.g. `roleid`) is an invitation to send that
  field back. Cheapest access control test that exists.
- The rendered page lies; the raw response tells the truth. Read every 3xx body
  in the Repeater before following the redirect.

## Pending

- Rename `08-data-leakage-in-response.md` → `08-data-leakage-in-redirect.md`
  (official lab name) and update the title inside the file.
- Writeups for the three "solved, writeup pending" labs — write them while the
  reasoning is fresh (sections 6 and 7 decay fast).
