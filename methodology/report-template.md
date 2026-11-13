# [Title]

- **Target:** 
- **Date:** 
- **Severity:** (CVSS: )
- **Affected endpoint:** 

## Summary
One paragraph. What is broken, in plain language.

## Impact
What can a real attacker do? Be specific: whose data, how many users, what privilege.

## Steps to reproduce
1. 
2. 
3. 

**Request:**
GET /api/v1/users/1234 HTTP/2 Host: target.com Authorization: Bearer 
**Response:**
200 OK {"id":1234,"email":"victim@corp.com"}

## Root cause
Why it happens (missing ownership check, trust in client-side value, etc.)

## Remediation
Concrete fix.

## References
