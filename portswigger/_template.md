# LAB: <exact lab name>

| | |
|---|---|
| **Topic** | <ex: SQL injection> |
| **Difficulty** | Apprentice / Practitioner / Expert |
| **Date** | YYYY-MM-DD |
| **Time** | <minutes> |
| **Solved without solution** | yes / no |
| **Link** | <lab url> |

## 1. Objective
What the lab asks for, in a sentence, with the words of the statement.
(and then: what you need to prove to yourself, not just to "Solved")

## 2. Surface
Where input goes: parameter, header, cookie, JSON body, path, form field.
How did you figure this out (proxy history, Burp browser, reading the request).

## 3. Hypothesis
"If I send X, I expect Y because Z."
Write the hypothesis **before** the payload. No hypothesis, you're kicking.

## 4. Payload that worked
<payload + encoding>
**Request:**
```
http
GET /path?param=payload HTTP/1.1
Host: target
Cookie: session=...
```

Response:
```
<result>
```

## 5. Why it works

The root cause: how the query/command/context is assembled, and why the payload breaks the logic. One or two sentences. If you can't explain it without looking at the solution, you didn't solve it — copy it.

## 6. What I tried that failed

Dead ends. This is the most valuable field in the file because it's the only one that only exists in your head. Ex: "' OR 1=1# failed → # is not a comment on this stack; - with space it worked."

## 7. In a real target (bounty translation)

Where does this actually appear and how would you test without going out of scope:

    Typical context: <ex: category filter in e-commerce>
    Quick detection: <ex: ' causes 500; '- normalizes; ' AND 1=2- deflates>
    Reportable impact: <ex: catalog filter bypass, hidden data enumeration>
    Probable severity: <Low/Medium/High> because <reason>


## 8. Bypass / variants noticed

Filters, WAF, encoding, XML encoding, CHAR(), case variation. Only what you actually tested or read in the topic material.

## 9. Takeaway (one line)

The phrase you want to reread in 6 months: "when you see X, test Y."
