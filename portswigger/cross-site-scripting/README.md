# Cross-Site Scripting (XSS)

Labs, notes, and takeaways for Cross-Site Scripting vulnerabilities: Reflected, Stored, and DOM-based XSS across HTML, Attribute, and JavaScript contexts.

## Labs

### Apprentice
- [x] Reflected XSS into HTML context with nothing encoded — [writeup](./01-reflected-html-nothing-encoded.md)
- [ ] Stored XSS into HTML context with nothing encoded — [writeup](./02-stored-html-nothing-encoded.md)
- [ ] DOM XSS in `document.write` sink using source `location.search` — [writeup](./03-dom-document-write-location-search.md)
- [ ] DOM XSS in `document.write` sink using source `location.search` inside a select element — [writeup](./04-dom-document-write-select-element.md)
- [ ] DOM XSS in `innerHTML` sink using source `location.search` in search blog — [writeup](./05-dom-innerhtml-location-search.md)
- [ ] DOM XSS in jQuery anchor `href` attribute sink using `location.search` source — [writeup](./06-dom-jquery-href-attribute.md)
- [ ] DOM XSS in jQuery selector attribute sink using back-button href — [writeup](./07-dom-jquery-selector-back-button.md)

### Practitioner
- [ ] Reflected XSS into HTML context with most untrusted tags blocked — [writeup](./08-reflected-html-tags-blocked.md)
- [ ] Reflected XSS into HTML context with all tags blocked except custom ones — [writeup](./09-reflected-html-custom-tags.md)
- [ ] Reflected XSS into event handlers with `<` and `>` HTML-encoded — [writeup](./10-reflected-event-handlers-encoded.md)
- [ ] Reflected XSS into attribute with angle brackets HTML-encoded — [writeup](./11-reflected-attribute-angle-brackets-encoded.md)
- [ ] Stored XSS into anchor `href` attribute with double quotes HTML-encoded — [writeup](./12-stored-href-attribute-double-quotes-encoded.md)
- [ ] Reflected XSS in canonical link tag — [writeup](./13-reflected-canonical-link-tag.md)
- [ ] Reflected XSS into a JavaScript string with single quote and backslash escaped — [writeup](./14-reflected-js-string-single-quote-backslash.md)
- [ ] Reflected XSS into a JavaScript string with angle brackets HTML-encoded — [writeup](./15-reflected-js-string-angle-brackets-encoded.md)
- [ ] Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded — [writeup](./16-reflected-js-string-angle-double-quotes-encoded.md)
- [ ] Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded — [writeup](./17-stored-onclick-event-encoded.md)
- [ ] Reflected XSS into a template literal with angle brackets, single, double quotes, and backslash escaped — [writeup](./18-reflected-template-literal-escaped.md)
- [ ] Exploiting XSS to perform CSRF — [writeup](./19-exploiting-xss-to-perform-csrf.md)
- [ ] Exploiting XSS to steal cookies — [writeup](./20-exploiting-xss-to-steal-cookies.md)
- [ ] Exploiting XSS to capture passwords — [writeup](./21-exploiting-xss-to-capture-passwords.md)

### Expert
- [ ] Reflected XSS with event handlers and attributes blocked — [writeup](./22-reflected-event-handlers-attributes-blocked.md)
- [ ] Reflected XSS with Content Security Policy (CSP) bypass — [writeup](./23-reflected-csp-bypass.md)
- [ ] Reflected XSS in a JavaScript URL with some characters blocked — [writeup](./24-reflected-js-url-characters-blocked.md)

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
