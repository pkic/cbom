---
layout: home
title: Overview
---

{% assign refs = site.data.references.references %}
{% assign total = refs | size %}
{% assign aspects = site.data.aspects.aspects %}
{% assign naspects = aspects | size %}
{% assign jset = refs | map: "jurisdiction" | uniq | size %}

<section class="hero">
  <div class="wrap hero-inner">
    <p class="eyebrow">PKI Consortium · Working Group</p>
    <h1 class="hero-title">CBOM&nbsp;Profiles<br><span class="accent">a neutral methodology for cryptography bills of materials</span></h1>
    <p class="hero-lede">
      The working home of the PKI Consortium CBOM Profiles Working Group. We are developing a
      single deliverable: a vendor-neutral, format-independent methodology for defining CBOM
      <em>profiles</em> — one that any sector can follow and that maps cleanly onto both
      CycloneDX and SPDX.
    </p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{{ '/issues/' | relative_url }}">See what we're working on</a>
      <a class="btn btn-ghost" href="{{ site.wg.charter }}">Read the charter</a>
    </div>
    <dl class="hero-stats">
      <div><dt>{{ naspects }}</dt><dd>methodology aspects</dd></div>
      <div><dt>2</dt><dd>working deliverables</dd></div>
      <div><dt>{{ total }}</dt><dd>reference sources</dd></div>
      <div><dt>{{ jset }}</dt><dd>jurisdictions tracked</dd></div>
    </dl>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <h2>What we're building</h2>
      <p>A profile, not another format.</p>
    </div>
    <div class="lead-columns">
      <p>
        A <strong>CBOM profile</strong> is a constrained, use-case-specific specification of
        what a Cryptography Bill of Materials should contain, how its fields are interpreted,
        and what validation rules apply. Our methodology describes how to define one —
        independently of any single base standard.
      </p>
      <p>
        Profiles are designed to <strong>map onto existing BOM standards</strong> such as
        CycloneDX and SPDX rather than compete with them. The PKIC output is intended to become
        the reference any industry consults when creating a CBOM profile for a particular use
        case.
      </p>
    </div>
  </div>
</section>

<section class="wrap cards-section">
  <div class="section-head">
    <h2>Explore the project</h2>
    <p>Four places to dig in.</p>
  </div>
  <div class="card-grid">
    <a class="feature-card" href="{{ '/issues/' | relative_url }}">
      <span class="card-kicker">{{ naspects }} aspects</span>
      <h3>Issues</h3>
      <p>The thirteen methodology aspects, each tracked as a discussion block. This is where
         the work happens — read a topic, weigh in, or raise one.</p>
      <span class="card-cta">Open the aspects &#8594;</span>
    </a>
    <a class="feature-card" href="{{ '/references/' | relative_url }}">
      <span class="card-kicker">{{ total }} sources</span>
      <h3>References</h3>
      <p>The evidence base — standards, regulation and guidance the methodology aligns to,
         filterable by category, status and jurisdiction.</p>
      <span class="card-cta">Browse the register &#8594;</span>
    </a>
    <a class="feature-card" href="{{ '/contributing/' | relative_url }}">
      <span class="card-kicker">No install required</span>
      <h3>Contributing</h3>
      <p>How to take part — join a discussion, raise an aspect topic, or add a reference. All
         in the browser, no command line.</p>
      <span class="card-cta">Read the guide &#8594;</span>
    </a>
    <a class="feature-card" href="{{ site.wg.url }}">
      <span class="card-kicker">PKI Consortium</span>
      <h3>Working group</h3>
      <p>The charter, membership and standing of the CBOM Profiles Working Group within the
         PKI Consortium.</p>
      <span class="card-cta">Visit the working group &#8599;</span>
    </a>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <h2>Why a profile is needed</h2>
      <p>The gap the methodology fills.</p>
    </div>
    <div class="lead-columns">
      <p>
        Almost every jurisdiction now requires organisations to hold
        <strong>a cryptographic inventory</strong>. Almost none of them says what that
        inventory should look like.
      </p>
      <p>
        India's CERT-In guidelines are the exception that proves the rule — they name the CBOM
        outright. Everywhere else the obligation is stated and the format is left open. A
        neutral CBOM profile is what turns "keep an inventory" into something producers and
        consumers can actually exchange and verify. The <a href="{{ '/references/' | relative_url }}">reference register</a>
        is the evidence base for that argument.
      </p>
    </div>
  </div>
</section>

<section class="wrap cards-section">
  <div class="section-head">
    <h2>How we work</h2>
    <p>Deliberation, decision and artifact are kept deliberately separate.</p>
  </div>
  <div class="inside-grid">
    <div class="inside-item">
      <h3>Deliberation</h3>
      <p>The open argument — options, trade-offs and questions — lives in a GitHub
         <a href="{{ site.repo.issues }}">Issue</a> or
         <a href="{{ site.repo.discussions }}">Discussion</a>.</p>
    </div>
    <div class="inside-item">
      <h3>Decision</h3>
      <p>The agreed outcome, with its reasoning, is captured as a short record in the
         <code>/decisions</code> folder — the project's permanent memory.</p>
    </div>
    <div class="inside-item">
      <h3>Artifact</h3>
      <p>The specification text itself changes only through a pull request, so every edit is
         reviewed line by line. We work by lazy consensus.</p>
    </div>
  </div>
</section>

<section class="wrap cta-section">
  <div class="cta-panel">
    <div>
      <h2>Take part</h2>
      <p>You don't need to be a developer or install anything. If you can use a web forum, you
         can contribute fully — pick an aspect and say your piece.</p>
    </div>
    <a class="btn btn-primary" href="{{ '/contributing/' | relative_url }}">How to contribute</a>
  </div>
</section>
