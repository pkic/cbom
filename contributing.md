---
title: Contributing
sideMenu: true
weight: 80
aliases:
- /cbom/contributing/
description: You don't need to be a developer, and you don't need to install anything.
  Most participation happens on GitHub in the browser; suggesting a reference is a
  simple email.
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

There are a few ways to take part, depending on what you want to do. Pick whichever fits — none of them requires editing files or using a command line.

Most common

### Weigh in on an aspect

Open the [Issues](../issues/) page, pick a topic, read from the top, and add your view in the comment box. A reaction emoji is a quick temperature check.

[Go to issues ↗](https://github.com/pkic/cbom/issues)

Open-ended

### Start a discussion

For a topic that hasn't narrowed to a single decision yet, open a [Discussion](https://github.com/pkic/cbom/discussions). It can be promoted to an aspect issue once it's ready to converge.

[Go to discussions ↗](https://github.com/pkic/cbom/discussions)

By email

### Suggest a reference

Spotted a standard, regulation or guidance we should track? Send a short note to the working-group mailing list — no GitHub account needed.

[How to suggest one ↓](#suggest-a-reference)

By email

### Suggest a tool

Know software that produces, reads or checks CBOMs? Send a link to where its maintainer says so, and it can be added to the tooling registry.

[How to suggest one ↓](#suggest-a-tool)

## Discuss the methodology

The methodology is built one aspect at a time, in the open. To take part:

-   **Catch up on a topic.** Open the [Issues](../issues/) page for the thirteen aspects, or the [Discussions](https://github.com/pkic/cbom/discussions) tab for open-ended threads. Click one and read from the top — the first post states the question, the comments are the conversation so far.
-   **Weigh in.** Scroll to the bottom of any issue or discussion, type in the comment box, and click the green button. To signal quick agreement without writing, use a reaction emoji.
-   **Raise a new topic.** A *specific question to settle* → the [Issues](https://github.com/pkic/cbom/issues) tab → **New issue** → the *Aspect topic* template. An *open-ended conversation* → [Discussions](https://github.com/pkic/cbom/discussions) → **New discussion**. If unsure, start a Discussion — it can become an Issue later.

We keep **deliberation** (issues and discussions), **decisions** (records in `/decisions`), and the **artifact** (the spec text, changed by pull request) deliberately separate, and we work by lazy consensus. The full lifecycle is in [CONTRIBUTING.md](https://github.com/pkic/cbom/blob/main/CONTRIBUTING.md).

## Suggest a reference

The [reference register](../references/) is curated by the working group. **You don't edit it directly** — instead, send the details to the CBOM mailing list and a maintainer will review the suggestion and fold it in.

**Email:** [cbom@lists.pkic.org](mailto:cbom@lists.pkic.org?subject=CBOM%20reference%20suggestion&body=Document%20title%20%26%20number%2Fversion%3A%0APublisher%20%2F%20organisation%3A%0APublication%20date%3A%0ALink%20to%20the%20primary%20source%3A%0AWhy%20it%20matters%20for%20CBOM%20work%20\(and%20does%20it%20name%20a%20format%3F\)%3A%0A) — subject line “CBOM reference suggestion”.

To make the suggestion easy to add, please include:

-   The document's **title** and its number or version (e.g. *BSI TR-03183-2 v2.1.0*)
-   The **publisher or organisation**
-   The **publication date**
-   A **link** to the primary source (the publisher's own page, not a mirror or vendor summary)
-   One or two lines on **why it matters** for CBOM work — and, importantly, whether it requires a cryptographic inventory and whether it **names a format**

[Email a reference suggestion ↗](mailto:cbom@lists.pkic.org?subject=CBOM%20reference%20suggestion&body=Document%20title%20%26%20number%2Fversion%3A%0APublisher%20%2F%20organisation%3A%0APublication%20date%3A%0ALink%20to%20the%20primary%20source%3A%0AWhy%20it%20matters%20for%20CBOM%20work%20\(and%20does%20it%20name%20a%20format%3F\)%3A%0A) [See the register](../references/)

Prefer GitHub? You can also open an issue on the [repository](https://github.com/pkic/cbom/issues) with the same details — whichever is easier for you.

## Suggest a tool

The [tooling registry](../tooling/) lists software that works with CBOMs. As with references, **you don't edit it directly**: send the details to the mailing list and a maintainer will add it. Suggestions for your own organisation's tools are welcome, and are held to the same rule as any other.

**Email:** [cbom@lists.pkic.org](mailto:cbom@lists.pkic.org?subject=CBOM%20tool%20suggestion&body=Tool%20name%3A%0AMaintainer%3A%0ALink%20to%20the%20repository%20or%20product%20page%3A%0ALink%20to%20where%20the%20maintainer%20states%20CBOM%20support%3A%0AWhat%20it%20does%20with%20a%20CBOM%20\(generate%2C%20consume%2C%20validate%2C%20convert%2C%20analyse\)%3A%0AFormats%20and%20versions%3A%0AOpen%20source%20or%20commercial%3A%0A) — subject line “CBOM tool suggestion”.

Please include:

-   The tool's **name** and **maintainer**
-   A link to its **repository or product page**
-   A link to **where the maintainer states CBOM support** — this is what gets a tool listed. A press release or a third-party article is a good lead, but the statement has to come from the maintainer's own material
-   **What it does with a CBOM** — generate, consume, validate, convert or analyse — and the **formats and versions** it names
-   Whether it is **open source** (and under which licence) or **commercial**

A listing is not an endorsement and is not a conformance result: the working group does not test the tools it lists.

## Come to a meeting

The [Meetings](../meetings/) page lists what is coming up and what the group has already worked through. An upcoming meeting carries its agenda, so you can see whether a topic you care about is being taken before you decide to attend; a past one carries the recording where one was made, and the [slides](../presentations/) presented, which you can download.

Meetings are open to working group members — see the [working group page](/wg/cbom/) for how to join. Nothing on this page other than this section needs a meeting: the aspects, the discussions and the reference suggestions all work asynchronously, and that is where most of the work happens.

## Edit the specification (optional, later)

When there is draft specification text to improve, you can propose a change straight from the browser: open the file, click the pencil ✏️ icon, make your edit, and click **Propose changes**. GitHub turns it into a pull request for others to review — you never touch a command line.

* * *

**For maintainers.** Edit the native pages `references.md`, `tooling.md`, `meetings.md`, and `presentations.md` through a reviewed content pull request. Keep source evidence, status, dates, authorship, recording restrictions, and stable entry IDs with each entry. The [publication guide](https://github.com/pkic/cbom/blob/main/PUBLICATION.md) describes the shared PKIC format and the coordinated cutover from the legacy site.
