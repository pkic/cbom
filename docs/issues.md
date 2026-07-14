---
layout: default
title: Issues
permalink: /issues/
eyebrow: CBOM Profiles · Working Group
heading: Issues
lede: The methodology is built one aspect at a time. Each aspect is a discussion block — a single question the working group needs to settle — tracked as a GitHub issue.
---

{% assign aspects = site.data.aspects.aspects %}

<div class="callout">
  <strong>New to how we work?</strong> A topic moves through four stages, shown by its
  <code>status:</code> label — <em>Raised → Deliberating → Converging → Decided</em>. Open
  exploration starts as a <a href="{{ site.repo.discussions }}">Discussion</a>; once it narrows
  to a concrete choice it becomes an <a href="{{ site.repo.issues }}">Issue</a>, which is closed
  and linked to the change that implements it. The decision rule is <strong>lazy consensus</strong>.
</div>

<p class="toolbar">
  <a class="btn btn-ghost" href="{{ site.repo.issues }}">All issues on GitHub &#8599;</a>
  <a class="btn btn-ghost" href="{{ site.repo.discussions }}">Discussions &#8599;</a>
  <a class="btn btn-ghost" href="{{ site.repo.issues }}/new/choose">Raise a topic &#8599;</a>
</p>

## The thirteen aspects

<p class="muted">
  From Section 3 of the scoping document, <em>Defining CBOM Profiles</em>. Each aspect has
  <strong>one</strong> canonical tracking issue — please comment on the existing thread rather
  than opening a parallel one.
</p>

{% assign status_labels = "raised:Raised,deliberating:Deliberating,converging:Converging,decided:Decided" | split: "," %}

<ol class="aspect-list">
{% for a in aspects %}
  <li class="aspect">
    <div class="aspect-top">
      <span class="aspect-sec">{{ a.section }}</span>
      <a class="aspect-title" href="{{ site.repo.url }}/issues/{{ a.issue }}">{{ a.title }}</a>
      <span class="badge badge-{{ a.status }}">{{ a.status | capitalize }}</span>
      {% if a.keystone %}<span class="flag flag-keystone" title="Settle this first — most aspects build on it">keystone</span>{% endif %}
      {% if a.crosscutting %}<span class="flag flag-cross" title="Discussed here and linked from other aspects">cross-cutting</span>{% endif %}
      {% if a.orientation == 'migration' %}<span class="flag flag-orient">migration</span>{% endif %}
    </div>
    <p class="aspect-summary">{{ a.summary }}</p>
    <p class="aspect-meta">
      <a href="{{ site.repo.url }}/issues/{{ a.issue }}">Issue #{{ a.issue }}</a>
      · orientation: {{ a.orientation }}
    </p>
  </li>
{% endfor %}
</ol>

## Where to start

<div class="rules">
  <div class="rule">
    <h3>Begin with 3.3</h3>
    <p>The format-independent attribute model underpins most other aspects — settling it first
       avoids rework.</p>
  </div>
  <div class="rule">
    <h3>3.6 and 3.7 are cross-cutting</h3>
    <p>Format mapping and normalisation are discussed in their own issues and linked from
       others, rather than re-argued in every thread.</p>
  </div>
  <div class="rule">
    <h3>3.10 is migration-flavoured</h3>
    <p>Roadmap and PQC-readiness information mainly concern migration-oriented profiles; related
       topics carry an <code>orientation:</code> label.</p>
  </div>
  <div class="rule">
    <h3>See the whole board</h3>
    <p>The <a href="{{ site.repo.board }}">project board</a> shows all thirteen at once, so you
       can see what's stuck, converging or decided at a glance.</p>
  </div>
</div>

<p class="muted note">
  Status and issue numbers here mirror the repository's start-here table. If they drift, the
  <a href="{{ site.repo.url }}/blob/main/README.md">README</a> and the live
  <a href="{{ site.repo.issues }}">issues</a> are authoritative.
</p>
