# LAB: User role can be modified in user profile

|                             |                                                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Topic**                   | Access control (vertical privilege escalation / mass assignment)                                                                                   |
| **Difficulty**              | Apprentice                                                                                                                                         |
| **Date**                    | 2026-11-12                                                                                                                                         |
| **Time**                    | 9                                                                                                                                                  |
| **Solved without solution** | yes                                                                                                                                                |
| **Link**                    | [lab-user-role-can-be-modified-in-user-profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile) |

## 1. Objective

Change my own role to administrator via the profile update endpoint and delete `carlos`.

## 2. Surface

`POST /my-account/change-email` with a **JSON** body. The response already returned
the user's `roleid` field-a sign that the user object is serialized and accepted
back by the endpoint.

## 3. Hypothesis

If the endpoint accepts the user object as JSON and does not filter fields, then
adding `roleid` to the body should update the role-mass assignment.

## 4. Payload that worked

Original request:

```json
{ "email": "wiener@normal-user.net" }
```

Modified request:

```json
{ "email": "wiener@normal-user.net", "roleid": 2 }
```

Response now shows `"roleid":2`. Then:

```http
GET /admin HTTP/1.1
Cookie: session=<session>
```

→ admin panel → GET /admin/delete?username=carlos → solved.

## 5. Why it works

The server performs automatic binding of the received JSON onto the User object, with no field whitelist. Any property on the model-including roleid-can be set by the client.

## 6. What I tried that failed

Before forging the body, I tried sending the role via query parameter and via cookie, with no effect. The endpoint doesn't read those places: it only consumes JSON.

Lesson: every endpoint has one input channel. Before testing, check the request's Content-Type-application/json means the body is the surface, and query/cookies are noise. The response already containing roleid was the hint for which field to forge.

## 7. In a real target (bounty translation)

Where it shows up: REST/JSON APIs with profile update, onboarding, checkout-anywhere that accepts a user object.
Quick detection: take the response of a GET on your own profile, copy the object, send it back on PUT/PATCH adding sensitive fields: role, roleid, isAdmin, verified, plan, credits, balance, tenantId.
Impact: vertical escalation and sometimes horizontal (tenantId) → High. Mass assignment on balance/credits can be Critical (financial impact).
In the report: the original body, the modified body, the response with the changed field, and the proof of privileged access. Comparer helps.

## 8. Bypass

If roleid is ignored, try role, roles:["admin"], isAdmin:true.
Try PATCH in addition to POST/PUT, and nested JSON ("user":{"roleid":2}).
Check whether the change persists after logout/login (proof of persistence).

## 9. Takeaway

If an API returns a field, it probably accepts that field back. Every profile response is an invitation to mass assignment: returning the object with one extra field is the cheapest access control test there is.
