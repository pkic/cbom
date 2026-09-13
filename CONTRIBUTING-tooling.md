# Maintaining the CBOM tooling registry

> **Suggesting a tool?** You don't edit this file. Email the details to the working-group
> mailing list — **cbom@lists.pkic.org** — or open an issue, and a maintainer will add it. See the
> [Contributing page](https://pkic.github.io/cbom/contributing/#suggest-a-tool) for what to
> include. The rest of this document is for the maintainers who fold those suggestions in.

The registry lives in **`docs/_data/tooling.yml`**. That file is the source of truth; the
published page at `/tooling/` is generated from it. Display labels for its fixed vocabularies
live under `labels:` in `docs/_config.yml`.

## What gets listed

A tool is listed when **its maintainer's own material states that it works with CBOMs** — the
repository, the documentation or the product page. That statement is the entry's `evidence`, and
it is the whole admission rule.

- A press release, analyst note, conference talk or third-party blog is not evidence. It is a
  lead: go and find the maintainer's own statement, and if there is none, do not list the tool.
- "Cryptographic discovery" or "crypto inventory" is not the same claim as CBOM support. List a
  discovery product only if it says it produces, imports or exports a CBOM, or CycloneDX
  cryptographic assets.
- Tools by working-group members are admitted on exactly the same rule, no more and no less.

## Adding a tool (maintainers)

1. Find the maintainer's statement of CBOM support and read it. Note the formats and versions it
   names, if any.
2. Append an entry to `tools:` in `docs/_data/tooling.yml`. Order in the file does not matter; the
   page sorts by name.
3. Run `python3 tests/check-site-data.py`.
4. Commit on a branch and open a pull request.

```yaml
  - id: example-scanner
    name: Example Scanner
    maintainer: Example Project
    url: https://github.com/example/scanner
    licensing: open-source
    license: Apache-2.0
    functions: [generate]
    methods: [source-code]
    formats: [CycloneDX 1.6]
    status: active
    summary: >-
      Scans Java source for calls into cryptographic APIs and writes the findings as a
      CycloneDX CBOM.
    evidence: https://github.com/example/scanner#readme
    checked: 2026-09-13
```

## Field reference

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Lowercase slug with hyphens. It is the page anchor (`/tooling/#id`). **Never reuse or rename.** Not `T1`: the Conformance section already uses T1–T7 for tool requirements. |
| `name` | yes | As the maintainer writes it. |
| `maintainer` | yes | The organisation or project. For a project hosted by a foundation, name the project and the foundation. |
| `url` | yes | The repository or the product page. Prefer the maintainer's own URL over a marketplace listing. |
| `licensing` | yes | `open-source`, `commercial` or `freemium`. |
| `license` | no | SPDX licence id. Expected when `licensing` is `open-source`; the checker notes its absence. |
| `functions` | yes | One or more of `generate`, `consume`, `validate`, `convert`, `analyse`, `visualise`, `store`. List the main one first: the page groups by it. |
| `methods` | no | Where a generator finds cryptography: `source-code`, `binary`, `container`, `filesystem`, `network`, `runtime`, `configuration`, `cloud`, `keystore`. Only on a tool that generates. |
| `formats` | no | Formats and versions **the source states**, e.g. `CycloneDX 1.6`. Leave it out rather than infer one. |
| `status` | yes | `active`, `archived` or `unknown`. An archived repository, or no release in two years, is `archived`. |
| `summary` | no | One or two sentences on what the tool does with a CBOM. |
| `evidence` | yes | The URL of the maintainer's statement of CBOM support. |
| `checked` | yes | The date you last read the evidence, not the date the entry was first added. |
| `verify` | no | `true` if a detail could not be confirmed. Renders a visible badge. |
| `tags` | no | Free-text list. |

Adding a value to `functions`, `methods`, `licensing` or `status` needs a display label under the
matching `labels.tool_*` key in `docs/_config.yml`; the checker fails an entry whose value has no
label.

## House rules

- **Describe, don't rank.** No "leading", "best", "comprehensive" or other language from the
  product page. The registry says what a tool does with a CBOM, and nothing about how well.
- **No conformance claims.** An entry never says a tool's output conforms to a profile. That is a
  verdict, and it belongs to a validator run over a named document, not to a directory listing.
- **Do not delete a tool that stops being maintained.** Set `status: archived`. Other documents and
  meeting notes may link to its anchor.
- **Re-check, and date it.** Tools change faster than standards. When you re-read an entry's
  evidence, update `checked`. The checker notes any entry not checked for a year.
- **Flag what you could not confirm** with `verify: true` rather than asserting it.

## Previewing locally

```bash
cd docs
bundle exec jekyll serve
```

Or open the pull request — GitHub Pages builds a preview on the branch.
