# Slovene proofreading

Pick from research (PICKS.md section 8): Claude as the proofreader, LanguageTool's public API as a mechanical second pass, Fran for doubtful words. No maintained Slovene grammar engine with an API exists. LanguageTool's Slovene rules are old (no edits since 2022) but still catch missing commas before "da" and many typos.

## 1. Claude pass (always)
Check, in this order:
1. **Spelling and typos**, including č/š/ž lost to an English keyboard (cas -> čas).
2. **Commas before subordinate clauses:** da, ker, ki, ko, če, kot (in a clause), čeprav, dokler, kjer, kar. And before contrast words: ampak, vendar, toda, a.
3. **"ne" apart from the verb:** ne vem, ne morem (except nisem, nimam, nočem).
4. **Case and number:** endings after numbers (2 kavi, 3 kave, 5 kav), dual for two (midva sva, dve kavi).
5. **s/z and k/h** before the next sound (s prijatelji, z mamo; k tebi, h gostom).
6. **Vikanje or tikanje** consistent through the whole text, including verb endings.
7. **Formats:** quotes „...“ or »...«; decimal comma (3,50 €); date 27. 10. 2026 with spaces; time 8.00 or 8:00, one style throughout.
8. **Anglicisms and calques** when a normal Slovene word exists (only flag; the user decides tone).

Do not rewrite style unless asked. Proofreading changes errors, not voice.

## 2. LanguageTool public API (second pass)
```bash
curl -s https://api.languagetool.org/v2/check \
  --data-urlencode "text@message.txt" \
  --data "language=sl-SI"
```
(`text@file` reads the text from a UTF-8 file; for a short string use `--data-urlencode "text=..."`.)

Read `matches[]`: `message`, `rule.id`, `offset`, `length`, `replacements[].value`. Common useful rules: `DA_BREZ_VEJICE` (missing comma before "da"), `MORFOLOGIK_RULE_SL_SI` (spelling).

Limits and terms (dev.languagetool.org/public-http-api, read 2026-10-27):
- 20 requests per IP per minute, 75 KB per minute, 20 KB per request. POST only.
- The page says not to send automated requests. Use it on request, one text at a time, never in loops or batch jobs. For volume, run LanguageTool locally (open source, Java) instead.
- Text goes to LanguageTool's servers. Do not send personal data, staff details or client-confidential text; check those with Claude and Fran only.

Treat LT hits as suggestions. Its spelling list misses names, brands and new words: reject those hits.

## 3. Fran lookups (doubtful words and usage)
- Search: `https://www.fran.si/iskanje?View=1&Query=<word>`
- One dictionary only: add `&FilteredDictionaryIds=<id>`. SSKJ2 = 133, Slovenski pravopis = 134, eSSKJ = 201, Jezikovna svetovalnica = 151.
- Full-text search (finds the word inside entries and advice answers): `&All=<word>`.
- Entry URLs look like `/134/slovenski-pravopis/<id>/<headword>`; cite that URL in the change list.

Use Fran when Claude and LT disagree, for unusual words, for whether a word is "knjižno", and for spelling of compounds and capitalisation. Jezikovna svetovalnica answers usage questions with reasons.

Terminology for EU or legal text: IATE (iate.europa.eu) in addition to Fran. Termania is non-commercial only, so not for business text.

## 4. Output
```
[corrected text]

Changes:
- "Mislim da" -> "Mislim, da": comma before da (LT DA_BREZ_VEJICE)
- "nevem" -> "ne vem": ne apart from the verb (Fran: Slovenski pravopis, <url>)
- ...
Not changed: [any hit rejected, with reason]
```
If nothing needed changing, say so in one line.

## Test before trusting it
DASSLE 1.0 (CLARIN.SI, 7,385 sentences with one error each, CC BY-NC-SA): take 50 sentences, score Claude alone against Claude + LT. Keep the LT pass only if it catches errors Claude misses.
