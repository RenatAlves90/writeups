# Recon Checklist

Objective: transform a domain into a testable surface, without noise and without going out of scope.
Rule: **scope first, tool later.**

---

## 0. First step

- [ ] I read the entire program`s policy (not just the asset list)
- [ ] List 1 domain and checked: is it in scope or is it `*` wildcard?
- [ ] I identified what is **out of scope** (third party subdomains, staging, docs, blog, CDN)
- [ ] I noted restrictions: rate limit, no DoS, no automated scan on login, no brute force
- [ ] I defined my **user-agent**-if the program requires identification, it is the correct one
- [ ] I know where to report (paid program, VDP, off-platform)
- [ ] I recorded start date/time in `bug-bounty/programs/<programa>/recon-notes.md`

## 1. Passive

- [ ] `subfinder -d target.com -all`
- [ ] `crt.sh` via curl (Certificate Transparency takes a subdomain that no other source has)
- [ ] `assetfinder --subs-only`
- [ ] ASN / company IP ranges (`whois -h whois.radb.net - `-i origin AS12345")
- [ ] Reverse whois / reverse IP (just to find other properties, confirm scope first)
- [ ] Shodan/Censys (free tier): `ssl:"alvo.com" 200`
- [ ] Google dork: `site:alvo.com -www`, `site:*.alvo.com filetype:pdf`
- [ ] Target GitHub: Search for `target.com` in code, secrets, internal endpoints
- [ ] Wayback Machine for old paths
- [ ] Check **company acquisitions** (old brands = forgotten surface)

## 2. Active

- [ ] `dnsx` to resolve the list
- [ ] `httpx -sc -title -td -cdn`-map what responds and with which stack
- [ ] Separate hosts by stack (WordPress / Jenkins / Grafana / Spring / Tomcat / Exchange)
- [ ] `naabu` top ports, then nmap only on hosts that deserve it
- [ ] Check non-web ports with HTTP (8080, 8443, 9000, 3000, 5601, 9200)
- [ ] Collect orphaned CNAMEs → `nuclei -tags takeover`
- [ ] Response headers on all hosts (version, server, X-Powered-By)

## 3. Application Surface

- [ ] `katana` with `-jc` (parse from JS) on all living hosts
- [ ] `gau --subs` + `waybackurls` for historical URLs
- [] Merge + dedupe
- [ ] Extract **parameters** (`grep `=")-are the raw material of IDOR/XSS/SSRF
- [ ] Extract **JS** files and look for endpoints, keys, tokens, internal rolls
- [ ] Extract sensitive files: `.env`, `.git/config`, `.bak`, `.old`, `.zip`, `.sql`, `swagger.json`, `actuator`
- [ ] Run `nuclei` by severity; read each match **manually** before reporting

## 4. Screening than the pipeline spits

For each item, decide: **is it a bug, is it noise, or is it a clue?**

- [ ] `nuclei` match → hand confirm (template false positive is cause no. 1 of N/A)
- [ ] 403 → is not "protected": test path traversal, `X-Original-URL`, `X-Rewrite-URL`, header bypass
- [ ] 401 in API → test without auth, weak auth, token from another account
- [ ] Exposed panel → try `admin:admin`, fetch credential from JS/GitHub before reporting
- [ ] `.js` → fetch `api/`, `internal`, `token`, `key`, `secret`, `admin`
- [ ] URL with `id=` → test IDOR with two accounts (horizontal swap)
- [ ] Old/infra subdomain → test software version, public CVE (banner first)
- [ ] Probable duplicate (obvious bug in giant target) → **go deeper**, not report the obvious

## 5. before writing the report

- [ ] I reproduced 2x from scratch, with numbered steps
- [ ] Real impact written in 1 sentence (who loses what)
- [ ] PoC: raw request + response, and video/GIF if the flow is multi-step
- [ ] I checked that it is not expected/documented behavior
- [ ] I checked the program`s Hacktivity: has it been reported before?
- [ ] Estimated severity with CVSS + justification
- [ ] No real third party data in PoC (mask PII)

---

## Guardrails

- Never run aggressive scan in production without the program allowing it
- Rate limit low at first; rise only if the target holds and policy allows it
- One target per day, one week per program-unfocused recon is waste
- Save everything in `output/<target>/` and summarize in `recon-notes.md` (the summary is what you reread)
