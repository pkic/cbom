---
layout: default
title: Tooling
permalink: /tooling/
eyebrow: CBOM Tooling Registry
heading: Tooling
lede: Software that generates, consumes, validates or analyses Cryptography Bills of Materials. Filter, search, or regroup the registry below.
---

{% assign tools = site.data.tooling.tools | sort_natural: "name" %}
{% assign total = tools | size %}

<div class="callout">
  <strong>A listing is not an endorsement.</strong> A tool is listed when its maintainer's own
  material states that it works with CBOMs, and each entry links to that statement. Nothing here
  has been tested by the working group: no entry is a claim that a tool's output conforms to a
  profile, and the tool requirements in the
  <a href="{{ '/methodology/conformance.html' | relative_url }}">Conformance</a> section are not
  assessed. Details change quickly — check the source before relying on one.
</div>

{% if total == 0 %}

<p class="empty">No tools have been listed yet. They appear here once an entry is added to
<a href="{{ site.repo.url }}/blob/main/docs/_data/tooling.yml"><code>docs/_data/tooling.yml</code></a>.</p>

{% else %}

<div class="controls" id="controls">
  <div class="control-bar">
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
        <circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="13.5" y1="13.5" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <input type="search" id="q" placeholder="Search names, maintainers, summaries, formats and tags…" aria-label="Search tools">
    </div>

    <select id="groupby" aria-label="Group results by">
      <option value="primary">Group by main function</option>
      <option value="licensing">Group by licensing</option>
      <option value="status">Group by status</option>
    </select>
  </div>

  <div class="filter-row">
    <span class="filter-label">Does</span>
    {% for f in site.labels.tool_function %}
      <button class="chip" data-facet="function" data-value="{{ f[0] }}">{{ f[1] }}</button>
    {% endfor %}
  </div>

  <div class="filter-row">
    <span class="filter-label">Licensing</span>
    {% for l in site.labels.tool_licensing %}
      <button class="chip" data-facet="licensing" data-value="{{ l[0] }}">{{ l[1] }}</button>
    {% endfor %}
    <button class="chip clear" id="clear" hidden>Clear filters</button>
  </div>

  <p class="count" id="count"></p>
</div>

<div id="results">
{% for t in tools %}
  {%- capture haystack -%}
    {{ t.name }} {{ t.maintainer }} {{ t.summary }} {{ t.license }} {{ t.formats | join: ' ' }} {{ t.functions | join: ' ' }} {{ t.methods | join: ' ' }} {{ t.tags | join: ' ' }}
  {%- endcapture -%}

  <article class="ref tool"
           id="{{ t.id }}"
           data-function="{{ t.functions | join: ' ' | escape }}"
           data-primary="{{ t.functions | first | escape }}"
           data-licensing="{{ t.licensing | escape }}"
           data-status="{{ t.status | escape }}"
           data-search="{{ haystack | strip_newlines | downcase | normalize_whitespace | escape }}">
    <div class="ref-head">
      <span class="doc">{{ site.labels.tool_licensing[t.licensing] }}{% if t.license %} · {{ t.license }}{% endif %}</span>
      <span class="badge badge-tool-{{ t.status }}">{{ site.labels.tool_status[t.status] }}</span>
      {% if t.verify %}<span class="badge badge-verify" title="A detail could not be confirmed against the primary source">verify</span>{% endif %}
    </div>

    <h3 class="ref-title"><a href="{{ t.url }}">{{ t.name }}</a></h3>

    <p class="meta">{{ t.maintainer }} · checked {{ t.checked | date: "%-d %b %Y" }}</p>

    {% if t.summary %}<p class="notes">{{ t.summary }}</p>{% endif %}

    <dl class="tool-facts">
      <div><dt>Does</dt><dd>{% for f in t.functions %}<span class="tag">{{ site.labels.tool_function[f] }}</span>{% endfor %}</dd></div>
      {% if t.methods %}<div><dt>Finds cryptography in</dt><dd>{% for m in t.methods %}<span class="tag">{{ site.labels.tool_method[m] }}</span>{% endfor %}</dd></div>{% endif %}
      {% if t.formats %}<div><dt>Formats</dt><dd>{% for f in t.formats %}<span class="tag">{{ f }}</span>{% endfor %}</dd></div>{% endif %}
    </dl>

    <p class="tool-evidence"><a href="{{ t.evidence }}">Where CBOM support is stated &#8599;</a></p>
  </article>
{% endfor %}
</div>

<p class="empty" id="empty" hidden>No tools match those filters.</p>

<script>
  window.CBOM_TOOL_LABELS = {
    primary: {{ site.labels.tool_function | jsonify }},
    licensing: {{ site.labels.tool_licensing | jsonify }},
    status: {{ site.labels.tool_status | jsonify }}
  };
</script>
<script src="{{ '/assets/js/tooling.js' | relative_url }}"></script>

{% endif %}

<p class="muted note">
  <strong>Know a tool that should be here, or an entry that is out of date?</strong> Email
  <a href="mailto:cbom@lists.pkic.org?subject=CBOM%20tool%20suggestion">cbom@lists.pkic.org</a>
  with a link to where its maintainer states CBOM support — see
  <a href="{{ '/contributing/' | relative_url }}#suggest-a-tool">Contributing</a>. Maintainers add
  entries to
  <a href="{{ site.repo.url }}/blob/main/docs/_data/tooling.yml"><code>docs/_data/tooling.yml</code></a>
  following <a href="{{ site.repo.url }}/blob/main/CONTRIBUTING-tooling.md">CONTRIBUTING-tooling.md</a>.
</p>
