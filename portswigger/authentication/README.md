# Authentication Vulnerabilities

Labs, notes, and takeaways for authentication vulnerabilities: username enumeration, password reset flaws, brute-force protections, multi-factor authentication bypasses, and logic flaws in login mechanisms.

## Labs

### Apprentice
- [x] Username enumeration via different responses — [writeup](./01-username-enumeration-via-different-responses.md)
- [x] 2FA simple bypass — [writeup](./02-2fa-simple-bypass.md)
- [ ] Insufficient password recovery — [writeup](./03-insufficient-password-recovery.md)

### Practitioner
- [x] Username enumeration via subtly different responses — [writeup](./04-username-enumeration-via-subtly-different-responses.md)
- [x] Username enumeration via response timing — [writeup](./05-username-enumeration-via-response-timing.md)
- [x] Broken brute-force protection, IP block — [writeup](./06-broken-brute-force-protection-ip-block.md)
- [x] Username enumeration via account lock — [writeup](./07-username-enumeration-via-account-lock.md)
- [x] 2FA broken logic — [writeup](./08-2fa-broken-logic.md)
- [ ] Brute-forcing a recovery token — [writeup](./09-brute-forcing-a-recovery-token.md)
- [ ] Password reset broken logic — [writeup](./10-password-reset-broken-logic.md)
- [ ] Password reset poisoning via middleware — [writeup](./11-password-reset-poisoning-via-middleware.md)
- [ ] Password brute-force via password change — [writeup](./12-password-brute-force-via-password-change.md)
- [ ] 2FA broken logic — [writeup](./13-2fa-broken-logic.md)
- [x] Brute-forcing a stay-logged-in cookie — [writeup](./14-brute-forcing-a-stay-logged-in-cookie.md)
- [x] Offline password cracking — [writeup](./15-offline-password-cracking.md)

### Expert
- [x] Broken brute-force protection, multiple credentials per request — [writeup](./16-broken-brute-force-protection-multiple-credentials-per-request.md)
- [x] 2FA bypass using a brute-force attack — [writeup](./17-2FA-bypass-using-a-brute-force-attack.md)

## Takeaways

Authentication asks a fundamental question: **can the application reliably prove who the user is before granting access?** If validation steps can be skipped, enumeration vectors are left open, or tokens are predictable and reusable, authentication collapses.

Checklist before any payload:

1. Map the entire authentication and recovery flow from end to end.
2. Identify where state is maintained (cookies, tokens, headers, session IDs).
3. Check for information leakage in error messages, status codes, response times, or headers.
4. Test whether intermediate verification steps (such as 2FA or password reset tokens) can be bypassed or brute-forced.

## Notes

- An authentication mechanism is only as strong as its weakest link: a secure password policy is useless if the recovery flow leaks tokens or allows easy enumeration.
- Always check response times and differential error handling; subtle timing or content changes often reveal valid usernames or internal system states.
- Multi-factor authentication flows must validate the second factor within the same authenticated session context; failing to tie the 2FA step tightly to the primary login session enables simple state-skipping bypasses.
