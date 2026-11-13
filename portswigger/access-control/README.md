# Access Control

Labs, notes, and takeaways for access control vulnerabilities: vertical and
horizontal privilege escalation, IDOR, and mass assignment.

## Labs

- [x] Unprotected admin functionality-Apprentice
- [x] Unprotected admin functionality with unpredictable URL-Apprentice
- [x] User role controlled by request parameter-Apprentice
- [x] User role can be modified in user profile-Apprentice
- [x] User ID controlled by request parameter-Apprentice
- [x] Insecure direct object references-Apprentice
- [x] User ID controlled by request parameter, with unpredictable user IDs-Apprentice
- [x] User ID controlled by request parameter with data leakage in response-Apprentice
- [ ] User ID controlled by request parameter with password disclosure-Apprentice
- [ ] URL-based access control can be circumvented-Practitioner
- [ ] Method-based access control can be circumvented-Practitioner

## Takeaways

Access control always asks the same question: **where does the server get the
identity and the permission from?** If the answer is "from what the client sent"
(path, query, body, cookie, header, JWT claim), it is IDOR or privilege escalation.

Checklist before any payload:

1. Read the **entire** request-path, query, body, headers, cookies
2. Identify which field carries identity or role, and in which channel it lives
3. Test with **two accounts**
4. Compare responses side by side (Burp Comparer)

## Notes

- `Content-Type: application/json` means the body is the surface-query and
  cookies are usually noise for that endpoint.
- A response that returns a field (e.g. `roleid`) is an invitation to send that
  field back. Cheapest access control test that exists.
