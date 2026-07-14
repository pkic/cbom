---
layout: default
title: Contributing
permalink: /contributing/
eyebrow: CBOM Profiles · Working Group
heading: Contributing
lede: You don't need to be a developer, and you don't need to install anything. Most participation happens on GitHub in the browser; suggesting a reference is a simple email.
---

There are a few ways to take part, depending on what you want to do. Pick whichever fits —
none of them requires editing files or using a command line.

<div class="card-grid contrib-grid">
  <div class="feature-card">
    <span class="card-kicker">Most common</span>
    <h3>Weigh in on an aspect</h3>
    <p>Open the <a href="{{ '/issues/' | relative_url }}">Issues</a> page, pick a topic, read
       from the top, and add your view in the comment box. A reaction emoji is a quick
       temperature check.</p>
    <a class="card-cta" href="{{ site.repo.issues }}">Go to issues &#8599;</a>
  </div>
  <div class="feature-card">
    <span class="card-kicker">Open-ended</span>
    <h3>Start a discussion</h3>
    <p>For a topic that hasn't narrowed to a single decision yet, open a
       <a href="{{ site.repo.discussions }}">Discussion</a>. It can be promoted to an aspect
       issue once it's ready to converge.</p>
    <a class="card-cta" href="{{ site.repo.discussions }}">Go to discussions &#8599;</a>
  </div>
  <div class="feature-card">
    <span class="card-kicker">By email</span>
    <h3>Suggest a reference</h3>
    <p>Spotted a standard, regulation or guidance we should track? Send a short note to the
       working-group mailing list — no GitHub account needed.</p>
    <a class="card-cta" href="#suggest-a-reference">How to suggest one &#8595;</a>
  </div>
</div>

## Discuss the methodology

The methodology is built one aspect at a time, in the open. To take part:

- **Catch up on a topic.** Open the [Issues]({{ '/issues/' | relative_url }}) page for the
  thirteen aspects, or the [Discussions]({{ site.repo.discussions }}) tab for open-ended
  threads. Click one and read from the top — the first post states the question, the comments
  are the conversation so far.
- **Weigh in.** Scroll to the bottom of any issue or discussion, type in the comment box, and
  click the green button. To signal quick agreement without writing, use a reaction emoji.
- **Raise a new topic.** A *specific question to settle* → the [Issues]({{ site.repo.issues }})
  tab → **New issue** → the *Aspect topic* template. An *open-ended conversation* →
  [Discussions]({{ site.repo.discussions }}) → **New discussion**. If unsure, start a
  Discussion — it can become an Issue later.

We keep **deliberation** (issues and discussions), **decisions** (records in `/decisions`), and
the **artifact** (the spec text, changed by pull request) deliberately separate, and we work by
lazy consensus. The full lifecycle is in [CONTRIBUTING.md]({{ site.repo.url }}/blob/main/CONTRIBUTING.md).

## Suggest a reference

The [reference register]({{ '/references/' | relative_url }}) is curated by the working group.
**You don't edit it directly** — instead, send the details to the CBOM mailing list and a
maintainer will review the suggestion and fold it in.

<div class="callout">
  <strong>Email:</strong> <a href="mailto:cbom@lists.pkic.org?subject=CBOM%20reference%20suggestion&amp;body=Document%20title%20%26%20number%2Fversion%3A%0APublisher%20%2F%20organisation%3A%0APublication%20date%3A%0ALink%20to%20the%20primary%20source%3A%0AWhy%20it%20matters%20for%20CBOM%20work%20(and%20does%20it%20name%20a%20format%3F)%3A%0A">cbom@lists.pkic.org</a>
  <span class="muted"> — subject line “CBOM reference suggestion”.</span>
</div>

To make the suggestion easy to add, please include:

- The document's **title** and its number or version (e.g. *BSI TR-03183-2 v2.1.0*)
- The **publisher or organisation**
- The **publication date**
- A **link** to the primary source (the publisher's own page, not a mirror or vendor summary)
- One or two lines on **why it matters** for CBOM work — and, importantly, whether it requires
  a cryptographic inventory and whether it **names a format**

<p class="toolbar">
  <a class="btn btn-ghost" href="mailto:cbom@lists.pkic.org?subject=CBOM%20reference%20suggestion&amp;body=Document%20title%20%26%20number%2Fversion%3A%0APublisher%20%2F%20organisation%3A%0APublication%20date%3A%0ALink%20to%20the%20primary%20source%3A%0AWhy%20it%20matters%20for%20CBOM%20work%20(and%20does%20it%20name%20a%20format%3F)%3A%0A">Email a reference suggestion &#8599;</a>
  <a class="btn btn-ghost" href="{{ '/references/' | relative_url }}">See the register</a>
</p>

<p class="muted">
  Prefer GitHub? You can also open an issue on the
  <a href="{{ site.repo.issues }}">repository</a> with the same details — whichever is easier
  for you.
</p>

## Edit the specification (optional, later)

When there is draft specification text to improve, you can propose a change straight from the
browser: open the file, click the pencil ✏️ icon, make your edit, and click **Propose
changes**. GitHub turns it into a pull request for others to review — you never touch a command
line.

<hr>

<p class="muted note">
  <strong>For maintainers.</strong> The register is a single data file,
  <a href="{{ site.repo.url }}/blob/main/docs/_data/references.yml"><code>docs/_data/references.yml</code></a>.
  Mailing-list suggestions are vetted and added following the field definitions and house rules
  in <a href="{{ site.repo.url }}/blob/main/CONTRIBUTING-references.md">CONTRIBUTING-references.md</a>.
</p>
