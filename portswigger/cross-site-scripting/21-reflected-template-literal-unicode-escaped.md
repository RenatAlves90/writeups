# LAB: Reflected XSS into a JavaScript template literal with angle brackets, single, double quotes, backslash and backticks escaped

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Cross-site scripting (XSS)                                                                                                    |
| **Difficulty**              | Practitioner                                                                                                                   |
| **Date**                    | 2026-11-26                                                                                                                     |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** | yes                                                                                                                             |
| **Link**                    | [lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped) |

## 1. Objective

Perform a Reflected Cross-Site Scripting (XSS) attack on a search feature where input is reflected inside a JavaScript template literal, and special characters (`<`, `>`, `'`, `"`, `\`, `` ` ``) are escaped or encoded, executing `alert()`.

## 2. Surface

- URL query parameter (`/search?search=...`).
- Server-side encoding and escaping filters targeting angle brackets, single/double quotes, backslashes, and backticks.
- Inline JavaScript template literal reflection context: Input reflected directly inside backticks (e.g., ``var searchTerms = `USER_INPUT`;``).

## 3. Hypothesis

If user input is reflected inside an ES6 template literal (enclosed in backticks `` ` ``) and the application escapes quote delimiters and backticks, an attacker does not need to break out of the string boundary. Template literals support native string interpolation via the `${...}` syntax. Since the JavaScript parser evaluates expressions inside `${}` prior to string construction, arbitrary code can be executed directly inside the template expression without breaking out of the surrounding string.

## 4. Payload that worked

Request:

Response:

## 5. Why it works

*(Aguardando o seu relato)*

## 6. What I tried that failed

*(Aguardando o seu relato)*

## 7. In a real target (bounty translation)

- Where it shows up: Dynamic frontend rendering engines, modern JavaScript single-page applications (SPAs), and inline script blocks using template strings for string formatting.
- Quick detection: Submit `${1+1}` into parameters reflected inside JavaScript blocks. Inspect the DOM to verify if the output resolves to `2` inside the template string.
- Impact: Reflected XSS execution bypassing typical quote and backslash filters.
- In the report: Document the template literal context, highlight the lack of `${}` expression filtering, and demonstrate the expression interpolation PoC.

## 8. Bypass / variants noticed

*(Aguardando o seu relato)*

## 9. Takeaway

Escaping quotes, backslashes, and backticks is insufficient when reflecting input into JavaScript ES6 template literals. Applications must sanitize or strip the `${}` interpolation syntax or use traditional string escaping and standard data binding models.
