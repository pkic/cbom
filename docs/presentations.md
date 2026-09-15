---
layout: default
title: Presentations
permalink: /presentations/
eyebrow: CBOM Profiles · Working Group
heading: Presentations
lede: Slides presented to the working group, and elsewhere on its behalf. Search or regroup the list, then download the deck.
---

{% assign decks = site.data.presentations.presentations | sort: "date" | reverse %}
{% assign total = decks | size %}
{% assign meetings = site.data.meetings.meetings %}

<p class="toolbar">
  <a class="btn btn-ghost" href="{{ '/meetings/' | relative_url }}">Meetings &#8594;</a>
  <a class="btn btn-ghost" href="{{ site.wg.url }}">Working group &#8599;</a>
</p>

{% if total == 0 %}

<p class="empty">No presentations have been published yet. They appear here once a deck is
added to <a href="{{ site.repo.url }}/blob/main/docs/_data/presentations.yml"><code>docs/_data/presentations.yml</code></a>.</p>

{% else %}

<div class="controls" id="controls">
  <div class="control-bar">
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
        <circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="13.5" y1="13.5" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <input type="search" id="q" placeholder="Search titles, presenters, summaries and tags…" aria-label="Search presentations">
    </div>

    <select id="groupby" aria-label="Group results by">
      <option value="meeting">Group by meeting</option>
      <option value="year">Group by year</option>
      <option value="presenter">Group by presenter</option>
    </select>

    <button class="chip clear" id="clear" hidden>Clear</button>
  </div>

  <p class="count" id="count"></p>
</div>

<div id="results">
{% for p in decks %}
  {%- comment -%}
    join handles both shapes: Liquid wraps a bare string in an array first, so a
    single presenter passes through unchanged and a list is comma-joined.
  {%- endcomment -%}
  {%- assign who = p.presenter | join: ", " -%}

  {%- assign mtitle = "" -%}
  {%- for m in meetings -%}
    {%- if m.number == p.meeting -%}{%- assign mtitle = m.title -%}{%- endif -%}
  {%- endfor -%}
  {%- if p.meeting -%}
    {%- capture group_meeting -%}Meeting #{{ p.meeting }}{% if mtitle != "" %} — {{ mtitle }}{% endif %}{%- endcapture -%}
  {%- else -%}
    {%- capture group_meeting -%}{{ p.venue | default: "Presented elsewhere" }}{%- endcapture -%}
  {%- endif -%}

  {%- if p.file -%}
    {%- assign ext = p.file | split: "." | last | upcase -%}
  {%- else -%}
    {%- assign ext = "" -%}
  {%- endif -%}
  {%- assign fmt = p.format | default: ext -%}

  {%- capture haystack -%}
    {{ p.title }} {{ who }} {{ p.org }} {{ p.summary }} {{ p.tags | join: ' ' }} {{ group_meeting }} {{ fmt }}
  {%- endcapture -%}

  <article class="deck"
           id="{{ p.id }}"
           data-meeting="{{ group_meeting | escape }}"
           data-year="{{ p.date | date: '%Y' }}"
           data-presenter="{{ who | escape }}"
           data-search="{{ haystack | strip_newlines | downcase | normalize_whitespace | escape }}">
    <div class="deck-head">
      <time class="deck-date" datetime="{{ p.date | date: '%Y-%m-%d' }}">{{ p.date | date: "%-d %b %Y" }}</time>
      {% if fmt != "" %}<span class="deck-fmt">{{ fmt }}</span>{% endif %}
      {% if p.filesize %}<span class="deck-size">{{ p.filesize }}</span>{% endif %}
      {% unless p.file %}<span class="badge badge-external" title="Hosted outside this site">external</span>{% endunless %}
      {% if p.example %}<span class="badge badge-example" title="Placeholder entry — replace or delete">example</span>{% endif %}
    </div>

    <h3 class="deck-title">{{ p.title }}</h3>

    <p class="meta">
      {{ who }}{% if p.org %} · {{ p.org }}{% endif %}
      {%- if p.meeting %} · <a href="{{ '/meetings/' | relative_url }}#meeting-{{ p.meeting }}">Meeting #{{ p.meeting }}</a>
      {%- elsif p.venue %} · {{ p.venue }}{% endif %}
    </p>

    {% if p.summary %}<p class="notes">{{ p.summary }}</p>{% endif %}

    {% if p.tags %}
    <p class="tags">{% for t in p.tags %}<span class="tag">{{ t }}</span>{% endfor %}</p>
    {% endif %}

    <p class="deck-actions">
      {% if p.file %}
        <a class="btn btn-primary" href="{{ '/assets/presentations/' | append: p.file | relative_url }}" download>Download{% if fmt != "" %} {{ fmt }}{% endif %} &#8595;</a>
        <a class="btn btn-ghost" href="{{ '/assets/presentations/' | append: p.file | relative_url }}">Open in browser</a>
      {% else %}
        <a class="btn btn-primary" href="{{ p.url }}">Open the deck &#8599;</a>
      {% endif %}
    </p>
  </article>
{% endfor %}
</div>

<p class="empty" id="empty" hidden>No presentations match that search.</p>

<script src="{{ '/assets/js/presentations.js' | relative_url }}"></script>

{% endif %}

<p class="muted note">
  <strong>For maintainers.</strong> Presentations are one data file,
  <a href="{{ site.repo.url }}/blob/main/docs/_data/presentations.yml"><code>docs/_data/presentations.yml</code></a>.
  A deck committed under <code>docs/assets/presentations/</code> is served from this site and its
  link cannot rot; one held elsewhere is linked with <code>url:</code> and marked
  <em>external</em>. Field definitions are in
  <a href="{{ site.repo.url }}/blob/main/CONTRIBUTING-meetings.md">CONTRIBUTING-meetings.md</a>.
</p>
