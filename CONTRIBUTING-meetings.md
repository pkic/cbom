# Maintaining meetings, presentations and polls

> **Want a deck published, or spotted something wrong?** You don't edit these files. Email the
> working-group mailing list — **cbom@lists.pkic.org** — or open an issue, and a maintainer will
> add it. The rest of this document is for the maintainers who do that.

Two data files drive two pages. No HTML or templates are involved.

| File | Page |
| --- | --- |
| `docs/_data/meetings.yml` | <https://pkic.github.io/cbom/meetings/> |
| `docs/_data/presentations.yml` | <https://pkic.github.io/cbom/presentations/> |

Presentation files themselves go in `docs/assets/presentations/`.

Run `python3 tests/check-site-data.py` before opening a pull request. CI runs it too.

## Upcoming and past are not a field

A meeting is Upcoming or Previous according to its `date`, worked out when the site is built.
There is no status to maintain and no way for the two to disagree.

The consequence worth knowing: **the split only moves when the site is rebuilt.** A meeting that
happened this morning still shows as Upcoming until the next push. In practice that is the same
push that adds the recording, so it takes care of itself — but if a meeting is going to sit
un-updated for a while, push something.

## Adding a meeting

1. Open `docs/_data/meetings.yml` and add an entry to `meetings:`.
2. Take the next `number`. Never reuse one — presentations reference meetings by number.
3. Give it a `date`, a `title`, and an `agenda` once there is one.
4. Commit on a branch and open a pull request.

```yaml
  - number: 3
    date: 2026-11-11
    time: "15:00"
    timezone: UTC
    duration: 60
    title: Attribute naming and profile composition
    join: https://...
    agenda:
      - Welcome, apologies, and approval of the previous minutes
      - "Q20 — whose names for algorithms should a CBOM use?"
      - Any other business
```

**Quote the time.** Unquoted, YAML reads `15:00` as a sexagesimal number and you get `900`. The
checker catches this, but quoting it is easier.

## After the meeting

1. Add `recording:` and `minutes:`, and a `summary:` of what was settled.
2. Remove `join:` — the link is usually dead, and leaving it invites someone to click it.
3. Add any presentations to `presentations.yml` with `meeting: <number>`.

If a meeting was deliberately not recorded, set `no_recording: true`. The page then says
"Not recorded" instead of "Recording to follow", which otherwise implies one is still coming.

If the recording is for PKI Consortium members only, set `recording_members_only: true` and do
**not** add `recording:`. This site is public, so a members-only link must not appear on it. The
page then says "Recording for members", and members find it where it was shared with them.

## Adding a presentation

An entry needs **exactly one** of `file:` or `url:`.

**`file:` — committed here, preferred.** The deck is served from this site and the link cannot
rot. Put the file in `docs/assets/presentations/`, named lowercase, hyphenated and dated:

```yaml
  - id: 2026-11-11-attribute-naming
    title: Attribute naming across two carriers
    date: 2026-11-11
    presenter: A. Presenter
    org: Example Corp
    meeting: 3
    file: 2026-11-11-attribute-naming.pdf
    filesize: "2.4 MB"
    summary: >-
      What the talk argued, in a sentence or two — not a restatement of the title.
```

**`url:` — held elsewhere.** Use this when the file is too large to commit sensibly, or belongs
to another body that publishes it itself. The page marks the entry *external*.

`presenter` may be one name or a list. `meeting` is optional — omit it for a deck given
somewhere else and use `venue:` instead, and the presentations page groups it under that.

### On committing binaries

A deck committed here is in the repository permanently, and git history does not shrink. A few
megabytes per meeting is fine. If a deck is large — video, or a deck heavy with images — use
`url:` instead. `.gitattributes` marks the usual presentation extensions `binary`, so they are
never line-ending-normalised.

## Polls

Many participants cannot use GitHub, so polls do not run on it. Votes are collected in
Formbricks, and `docs/_data/polls.yml` records what was asked and what came out. The meetings
page lists open polls above the upcoming meetings and results below the previous ones.

**Each member votes through a personal single-use link.** The link works once and needs no
account. Because it works once, it is never put on the site or in the repository. The site says
how to vote; the link arrives by email.

1. **Prepare.** Add the entry to `polls.yml` with `published: false`. Write each question as a
   proposal, with Agree, Disagree and Abstain unless the question needs other options. Set
   `closes` before the meeting that will act on the result.
2. **Create the survey** in Formbricks with the same questions and options, in the same order.
   Turn on single-use links and generate one per member.
3. **Send the links** from the working group mailing list, one per member, with the closing
   date. Then set `published: true` and commit. The poll appears on the meetings page.
4. **After it closes,** add `result`: the number of links sent (`invited`), the number of
   completed responses, the counts per question, and an `outcome` of one or two sentences. If
   the result settles something, record it in the decision log and name it in `recorded`.

A poll where it does not matter who votes or how often can use `access: open` with a public
`url` instead. Use that sparingly.

The checker enforces the two rules that matter most: a single-use poll carries no `url`, and a
poll shows no result before it has closed.

## Field reference

### `meetings.yml`

| Field | Required | Notes |
| --- | --- | --- |
| `number` | yes | Sequential integer. **Never reuse** — presentations reference it. |
| `date` | yes | `YYYY-MM-DD`, unquoted. Decides Upcoming vs Previous. |
| `title` | yes | What the meeting is about, in a few words. |
| `time` | no | `"HH:MM"` — **quoted**. |
| `timezone` | no | Defaults to `meta.timezone`. |
| `duration` | no | Minutes. |
| `agenda` | no | List of items. Expected on an upcoming meeting. |
| `join` | no | Upcoming only. Remove it afterwards. |
| `recording` | no | Past only. |
| `no_recording` | no | `true` when the meeting was deliberately not recorded. |
| `recording_members_only` | no | `true` when a recording exists but is for members only. Never combine with `recording`. |
| `minutes` | no | Link to minutes or notes. |
| `summary` | no | One to three sentences on what was settled. |
| `example` | no | `true` marks a placeholder. Renders a badge; delete once real meetings exist. |

### `presentations.yml`

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Stable key, lowercase, date-prefixed. **Never reuse or rename** — it is the page anchor. |
| `title` | yes | The title of the talk. |
| `date` | yes | `YYYY-MM-DD`. |
| `presenter` | yes | A name, or a list of names. |
| `file` *or* `url` | yes | Exactly one. See above. |
| `org` | no | The presenter's organisation. |
| `meeting` | no | A `number` from `meetings.yml`. Both pages then cross-link. |
| `venue` | no | Where it was given, when it was not a working group meeting. |
| `format` | no | `PDF`, `PPTX`. Defaults to the file extension. |
| `filesize` | no | `"2.4 MB"`. **Not `size`** — see below. |
| `summary` | no | One to three sentences on what the talk argued. |
| `tags` | no | Free-text list. |
| `example` | no | `true` marks a placeholder. |

### `polls.yml`

The field definitions are at the top of the file. In short:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Lowercase slug. The page anchor is `#poll-<id>`. |
| `title` | yes | Short name. |
| `opens`, `closes` | yes | Dates. Open or closed is derived from `closes` at build time. |
| `access` | yes | `single-use` (no `url`) or `open` (with `url`). |
| `published` | no | `false` until the links have gone out. |
| `meeting` | no | The meeting that raised the questions. Both entries link to each other. |
| `questions` | yes | Each with `id`, `text`, at least two `options`, and optionally `comment: true`. |
| `result` | after closing | `invited`, `responses`, `counts`, `outcome`, optionally `recorded`. |

## House rules

- **Never reuse a meeting `number` or a presentation `id`.** Both are linked to from the other
  page and from anywhere else that cites them.
- **Say what was settled, not what was discussed.** A `summary` that reads "we talked about
  naming" tells a reader nothing they could not guess from the agenda.
- **Do not use `size:` on a presentation.** `size` is a reserved Liquid property: on an entry
  that lacks the key, `p.size` quietly renders the *number of fields* rather than nothing. The
  field is called `filesize` for that reason, and the checker rejects `size:`.
- **Delete the placeholder entries** once there are real meetings to list. They are marked
  `example: true` and render a visible badge so they cannot be mistaken for real ones.

## Previewing locally

```bash
cd docs
bundle exec jekyll serve   # or open the pull request — GitHub Pages builds a branch preview
```
