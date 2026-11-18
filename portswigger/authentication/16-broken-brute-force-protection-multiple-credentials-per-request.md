# LAB: Broken brute-force protection, multiple credentials per request

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-17                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-broken-brute-force-protection-multiple-credentials-per-request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request) |

## 1. Objective

Determine the password for the target account (`carlos`) by exploiting an authentication endpoint that accepts multiple candidate passwords within a single JSON request structure to bypass rate limiting.

## 2. Surface

- Login endpoint (`/login`) processing JSON-formatted POST request bodies.
- Authentication backend parsing arrays or batch payloads within parameter fields.
- Rate-limiting mechanism enforcing request-count thresholds rather than payload-count thresholds.

## 3. Hypothesis

If the authentication parser accepts an array of strings for the password field instead of a single scalar string, and evaluates each element sequentially against the specified account within a single HTTP connection, an attacker can bypass request-rate controls by testing an entire dictionary of passwords inside one request.

## 4. Payload that worked

Request:
```http
POST /login HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 1200
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Content-Type: application/json
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: */*
Origin: https://<host>.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://<host>.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=1, i


{
  "username":"carlos",
  "password":[
    "1",
    "2","123456",
    ...
  ]
}
```

Response:
```http
HTTP/2 302 Found
Location: /my-account?id=carlos
Set-Cookie: session=sess; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application's JSON parser accepts arrays as valid data structures within the `password` field without proper type validation. Because the authentication backend iterates over elements inside the provided password array and tests each against the specified user (`carlos`) within a single execution cycle, all payload candidates are processed in one HTTP request. Since rate-limiting rules were configured to track total incoming HTTP requests rather than individual credential evaluations, sending all wordlist entries inside a single array executes a high-volume brute-force attack without triggering request-count thresholds.
## 6. What I tried that failed

- Tested wrapping the entire request payload inside a JSON array of objects `[{"username": "carlos", "password": "..."}]`, which resulted in an HTTP `500 Internal Server Error` due to structural mismatch in the backend API parser.
- Rule extracted: When probing JSON endpoints for array-handling vulnerabilities, test parameter-level array injection (e.g., `"password": [...]`) separately from root-level request array structures.
  
## 7. In a real target (bounty translation)

- Where it shows up: JSON-based authentication APIs (REST/GraphQL) where data deserializers convert arrays directly into iterable backend types, combined with rate limiters configured to count incoming HTTP connections rather than total evaluated attempts.
- Quick detection: Pass an array of values `["val1", "val2"]` into parameter fields expected to be strings to observe if the endpoint processes the structure without throwing a 400 Bad Request or validation error.
- Impact: Complete evasion of request-based brute-force protections, allowing execution of large password dictionaries in a single network round-trip.
- In the report: Demonstrate the accepted JSON structure containing multiple payload items alongside server responses showing authentication state resolution.

## 8. Bypass / variants noticed

- Testing single-element arrays `{"password": ["test"]}` first to confirm whether parameter-level arrays trigger validation errors or return standard authentication responses (e.g., "invalid password") before supplying full wordlists.
- Combining batch parameter payloads with chunked requests or large JSON bodies to test backend memory limits alongside authentication rate-limit bypasses.
  
## 9. Takeaway

Authentication APIs processing structured formats (JSON/XML/GraphQL) must validate input data types strictly before passing them to authentication logic. Rate-limiting and lockout systems must monitor the number of evaluated credential pairs rather than rely solely on HTTP request counts.
