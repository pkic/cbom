---
layout: default
title: References
permalink: /references/
eyebrow: CBOM Reference Register
heading: References
lede: Standards, regulation and guidance relevant to Cryptography Bills of Materials. Filter, search, or regroup the register below.
---

{% assign refs = site.data.references.references %}
{% assign total = refs | size %}

<div class="controls" id="controls">
  <input type="search" id="q" placeholder="Search titles, organisations, notes…" aria-label="Search references">

  <div class="filter-row">
    <span class="filter-label">Category</span>
    {% for c in site.labels.category %}
      <button class="chip" data-facet="category" data-value="{{ c[0] }}">{{ c[1] }}</button>
    {% endfor %}
  </div>

  <div class="filter-row">
    <span class="filter-label">Status</span>
    {% for s in site.labels.status %}
      <button class="chip" data-facet="status" data-value="{{ s[0] }}">{{ s[1] }}</button>
    {% endfor %}
  </div>

  <div class="filter-row">
    <span class="filter-label">Jurisdiction</span>
    {% for j in site.labels.jurisdiction %}
      <button class="chip" data-facet="jurisdiction" data-value="{{ j[0] }}">{{ j[1] }}</button>
    {% endfor %}
  </div>

  <div class="filter-row">
    <span class="filter-label">Group by</span>
    <button class="chip toggle is-on" data-group="category">Category</button>
    <button class="chip toggle" data-group="jurisdiction">Jurisdiction</button>
    <button class="chip clear" id="clear">Clear all</button>
  </div>

  <p class="count" id="count"></p>
</div>

<div id="results">
{% for r in refs %}
  {%- comment -%}
    Build the search haystack separately, then escape it. Notes and titles contain
    double quotes (e.g. "as soon as practicable"), which would otherwise terminate
    the data-search attribute and corrupt the markup.
  {%- endcomment -%}
  {%- capture haystack -%}
    {{ r.id }} {{ r.doc }} {{ r.title }} {{ r.org }} {{ r.notes }} {{ r.tags | join: ' ' }}
  {%- endcapture -%}

  <article class="ref"
           data-id="{{ r.id | escape }}"
           data-category="{{ r.category | escape }}"
           data-status="{{ r.status | escape }}"
           data-jurisdiction="{{ r.jurisdiction | escape }}"
           data-search="{{ haystack | strip_newlines | downcase | normalize_whitespace | escape }}">
    <div class="ref-head">
      <span class="cite">[{{ r.id }}]</span>
      <span class="doc">{{ r.doc }}</span>
      <span class="badge badge-{{ r.status }}">{{ site.labels.status[r.status] }}</span>
      {% if r.verify %}<span class="badge badge-verify" title="Confirm against the primary source before citing">verify</span>{% endif %}
    </div>

    <h3 class="ref-title">
      {% if r.url %}<a href="{{ r.url }}">{{ r.title }}</a>{% else %}{{ r.title }}{% endif %}
    </h3>

    <p class="meta">
      {{ r.org }}{% if r.date %} · {{ r.date }}{% endif %}
      · <span class="juris">{{ site.labels.jurisdiction[r.jurisdiction] }}</span>
    </p>

    {% if r.notes %}<p class="notes">{{ r.notes }}</p>{% endif %}

    {% if r.tags %}
    <p class="tags">{% for t in r.tags %}<span class="tag">{{ t }}</span>{% endfor %}</p>
    {% endif %}
  </article>
{% endfor %}
</div>

<p class="empty" id="empty" hidden>No references match those filters.</p>

<script>
  window.CBOM_LABELS = {
    category: {{ site.labels.category | jsonify }},
    jurisdiction: {{ site.labels.jurisdiction | jsonify }}
  };
</script>
<script src="{{ '/assets/js/references.js' | relative_url }}"></script>
