---
layout: home
title: Overview
---

{% assign refs = site.data.references.references %}
{% assign total = refs | size %}
{% assign policy = refs | where: "category", "policy" | size %}
{% assign formats = refs | where: "category", "formats" | size %}
{% assign methodology = refs | where: "category", "methodology" | size %}
{% assign jset = refs | map: "jurisdiction" | uniq | size %}

<section class="hero">
  <div class="wrap hero-inner">
    <p class="eyebrow">PKI Consortium · CBOM Profiles Working Group</p>
    <h1 class="hero-title">The reference base for<br><span class="accent">Cryptography Bills of Materials</span></h1>
    <p class="hero-lede">
      A single, maintained register of the standards, regulations and guidance that
      shape how organisations inventory their cryptography — curated to underpin a
      neutral, format-independent CBOM profile methodology.
    </p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{{ '/references/' | relative_url }}">Browse the references</a>
      <a class="btn btn-ghost" href="{{ '/contributing/' | relative_url }}">Contribute an entry</a>
    </div>
    <dl class="hero-stats">
      <div><dt>{{ total }}</dt><dd>curated references</dd></div>
      <div><dt>{{ jset }}</dt><dd>jurisdictions</dd></div>
      <div><dt>{{ policy }}</dt><dd>regulations &amp; guidance</dd></div>
      <div><dt>{{ formats | plus: methodology }}</dt><dd>standards &amp; methodology</dd></div>
    </dl>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <h2>Why this register exists</h2>
    </div>
    <div class="lead-columns">
      <p>
        Almost every jurisdiction now requires organisations to hold
        <strong>a cryptographic inventory</strong>. Almost none of them says what that
        inventory should look like.
      </p>
      <p>
        India's CERT-In guidelines are the notable exception — they name the CBOM
        outright. Everywhere else, from the EU's NIS Cooperation Group roadmap to the
        UK's NCSC timelines, US OMB M-23-02 and Singapore's MAS advisory, the obligation
        is stated and the format is left open. That gap is the case for a CBOM profile
        methodology, and this register is the evidence base for it.
      </p>
    </div>
  </div>
</section>

<section class="wrap cards-section">
  <div class="section-head">
    <h2>Explore the site</h2>
    <p>Three pages, one source of truth.</p>
  </div>
  <div class="card-grid">
    <a class="feature-card" href="{{ '/references/' | relative_url }}">
      <span class="card-kicker">{{ total }} entries</span>
      <h3>References</h3>
      <p>The full register — filterable by category, status and jurisdiction, with
         instant search and a group-by toggle.</p>
      <span class="card-cta">Open the register &#8594;</span>
    </a>
    <a class="feature-card" href="{{ '/contributing/' | relative_url }}">
      <span class="card-kicker">YAML &amp; pull requests</span>
      <h3>Contributing</h3>
      <p>How to add or amend a reference in one YAML block, the field definitions, and
         the house rules that keep the register honest.</p>
      <span class="card-cta">Read the guide &#8594;</span>
    </a>
    <a class="feature-card" href="{{ site.wg.url }}">
      <span class="card-kicker">PKI Consortium</span>
      <h3>CBOM Profiles WG</h3>
      <p>The working group developing the neutral methodology that maps CBOM profiles
         onto CycloneDX and SPDX.</p>
      <span class="card-cta">Visit the working group &#8599;</span>
    </a>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <h2>What's inside</h2>
      <p>Every entry is a structured record, not just a link.</p>
    </div>
    <div class="inside-grid">
      <div class="inside-item">
        <h3>BOM formats &amp; specifications</h3>
        <p>CycloneDX, the Cryptography Registry, ECMA-424, SPDX and the conformance
           vocabulary a profile is written against.</p>
      </div>
      <div class="inside-item">
        <h3>Methodology &amp; sector work</h3>
        <p>The PKIC methodology, the PQCC materials, GSMA telecom work, and the tooling
           that produces and analyses CBOMs.</p>
      </div>
      <div class="inside-item">
        <h3>Regulation &amp; guidance</h3>
        <p>EU, US, UK, Canada and Asia-Pacific mandates — each tagged for whether it
           requires an inventory and whether it names a format.</p>
      </div>
    </div>
  </div>
</section>

<section class="wrap cta-section">
  <div class="cta-panel">
    <div>
      <h2>Keep the register current</h2>
      <p>Spotted a new mandate, or a version that has moved on? Adding it is a single
         YAML entry and a pull request.</p>
    </div>
    <a class="btn btn-primary" href="{{ '/contributing/' | relative_url }}">How to contribute</a>
  </div>
</section>
