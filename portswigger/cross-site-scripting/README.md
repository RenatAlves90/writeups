# Cross-Site Scripting (XSS)

Labs, notes, and takeaways for Cross-Site Scripting vulnerabilities: Reflected, Stored, and DOM-based XSS across HTML, Attribute, and JavaScript contexts.

## Labs

### Apprentice
- [x] Reflected XSS into HTML context with nothing encoded — [writeup](./01-reflected-html-nothing-encoded.md)
- [x] Stored XSS into HTML context with nothing encoded — [writeup](./02-stored-html-nothing-encoded.md)
- [x] DOM XSS in `document.write` sink using source `location.search` — [writeup](./03-dom-document-write-location-search.md)
- [x] DOM XSS in `innerHTML` sink using source `location.search` — [writeup](./04-dom-innerhtml-location-search.md)
- [x] DOM XSS in jQuery anchor `href` attribute sink using `location.search` source — [writeup](./05-dom-jquery-href-attribute.md)
- [x] DOM XSS in jQuery selector sink using a hashchange event — [writeup](./06-dom-jquery-selector-hashchange.md)
- [x] Reflected XSS into attribute with angle brackets HTML-encoded — [writeup](./07-reflected-angle-brackets-html-encoded.md)
- [x] Stored XSS into anchor `href` attribute with double quotes HTML-encoded — [writeup](./08-stored-href-attribute-double-quotes-encoded.md)
- [ ] Reflected XSS into a JavaScript string with angle brackets HTML encoded — [writeup](./09-reflected-js-string-angle-brackets-encoded.md)

### Practitioner
- [x] DOM XSS in `document.write` sink using source `location.search` inside a select element — [writeup](./10-dom-document-write-select-element.md)
- [x] DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded — [writeup](./11-dom-xss-angularjs-brackets-double-quotes.md)
- [x] Reflected DOM XSS — [writeup](./12-reflected-dom-xss.md)
- [x] Stored DOM XSS — [writeup](./13-stored-dom-xss.md)
- [x] Reflected XSS into HTML context with most tags and attributes blocked — [writeup](./14-reflected-html-tags-and-attributes-blocked.md)
- [x] Reflected XSS into HTML context with all tags blocked except custom ones — [writeup](./15-reflected-html-all-tags-blocked-except-custom.md)
- [x] Reflected XSS with some SVG markup allowed — [writeup](./16-reflected-svg-markup-allowed.md)
- [x] Reflected XSS in canonical link tag — [writeup](./17-reflected-canonical-link-tag.md)
- [ ] Reflected XSS into a JavaScript string with single quote and backslash escaped — [writeup](./18-reflected-js-string-single-quote-backslash.md)
- [ ] Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped — [writeup](./19-reflected-js-string-angle-double-quotes-single-quote.md)
- [ ] Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped — [writeup](./20-stored-onclick-event-encoded.md)
- [ ] Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped — [writeup](./21-reflected-template-literal-unicode-escaped.md)
- [ ] Exploiting cross-site scripting to steal cookies — [writeup](./22-exploiting-xss-to-steal-cookies.md)
- [ ] Exploiting cross-site scripting to capture passwords — [writeup](./23-exploiting-xss-to-capture-passwords.md)
- [ ] Exploiting XSS to bypass CSRF defenses — [writeup](./24-exploiting-xss-to-bypass-csrf-defenses.md)
- [ ] Reflected XSS protected by very strict CSP, with dangling markup attack — [writeup](./25-reflected-strict-csp-dangling-markup.md)

### Expert
- [ ] Reflected XSS with AngularJS sandbox escape without strings — [writeup](./26-reflected-angularjs-sandbox-without-strings.md)
- [ ] Reflected XSS with AngularJS sandbox escape and CSP — [writeup](./27-reflected-angularjs-sandbox-and-csp.md)
- [x] Reflected XSS with event handlers and href attributes blocked — [writeup](./28-reflected-event-handlers-href-attributes-blocked.md)
- [ ] Reflected XSS in a JavaScript URL with some characters blocked — [writeup](./29-reflected-js-url-characters-blocked.md)
- [ ] Reflected XSS protected by CSP, with CSP bypass — [writeup](./30-reflected-csp-bypass.md)

## Takeaways

XSS analysis always answers two fundamental questions: **Where is the input reflected?** and **How is the client engine interpreting that specific context?** If execution succeeds, it is because input breaking syntax rules was rendered without context-appropriate sanitization or encoding.

Checklist before any payload:

1. Locate the exact reflection point in the raw HTTP response (HTML body, tag attribute, URL scheme, or `<script>` block).
2. Inspect how special characters (`<`, `>`, `"`, `'`, `\`, `/`) are handled by sending a test canary (e.g., `test"'><i>x1</i>`).
3. Match the payload strictly to the surrounding syntax (e.g., break out of attributes with quotes/events, or break out of JS strings with quotes/operators).
4. Verify execution context (alert, exfiltration via `fetch()`, or DOM manipulation) without relying solely on simple `<script>` tags.

## Notes

- HTML entity encoding (`&lt;`, `&gt;`) neutralizes tags in the body context, but won't prevent execution inside JavaScript code blocks or `javascript:` URI handlers.
- When angle brackets are encoded inside HTML attributes, focus on breaking the attribute context using quotes and injecting inline event handlers (`onfocus`, `onload`).
- Background exfiltration via `fetch()` or `XMLHttpRequest` is preferred over full browser redirects (`document.location`) because it captures data silently without disrupting the user session.
