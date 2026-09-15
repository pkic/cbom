---
layout: default
title: Meetings
permalink: /meetings/
eyebrow: CBOM Profiles · Working Group
heading: Meetings
lede: When the working group meets, what it plans to settle, and what it settled last time. Upcoming meetings carry an agenda; past meetings carry a recording where one was made.
---

{% assign all = site.data.meetings.meetings | sort: "date" %}
{% assign today = site.time | date: "%Y-%m-%d" %}
{% assign decks = site.data.presentations.presentations %}
{% assign tz = site.data.meetings.meta.timezone | default: "UTC" %}

{%- comment -%}
  Upcoming and past are derived from the date at build time, not stored. A meeting
  therefore moves to Past on the first build after it happens — in practice the commit
  that adds its recording. Both sides of the comparison are normalised to an ISO string
  so it holds whether YAML parsed `date` as a date or as text.
{%- endcomment -%}
{%- assign n_up = 0 -%}{%- assign n_past = 0 -%}
{%- for m in all -%}
  {%- assign md = m.date | date: "%Y-%m-%d" -%}
  {%- if md >= today -%}{%- assign n_up = n_up | plus: 1 -%}{%- else -%}{%- assign n_past = n_past | plus: 1 -%}{%- endif -%}
{%- endfor -%}

<div class="callout">
  <strong>Taking part.</strong> {{ site.data.meetings.meta.cadence }} Meetings are open to
  working group members — see the <a href="{{ site.wg.url }}">working group page</a> for how to
  join, and <a href="{{ '/contributing/' | relative_url }}">Contributing</a> for the ways to take
  part that need no meeting at all. Times are {{ tz }} unless an entry says otherwise.
</div>

<p class="toolbar">
  <a class="btn btn-ghost" href="{{ '/presentations/' | relative_url }}">Presentations &#8594;</a>
  <a class="btn btn-ghost" href="{{ site.repo.discussions }}">Discussions &#8599;</a>
  <a class="btn btn-ghost" href="{{ site.wg.url }}">Working group &#8599;</a>
</p>

## Upcoming <span class="group-count">{{ n_up }}</span>

{% if n_up == 0 %}
<p class="empty">No meeting is scheduled. The <a href="{{ site.wg.url }}">working group page</a> carries the current schedule.</p>
{% endif %}

<ol class="meeting-list">
{% for m in all %}
{% assign md = m.date | date: "%Y-%m-%d" %}
{% if md >= today %}
  {% assign mdecks = decks | where: "meeting", m.number %}
  <li class="meeting meeting-upcoming" id="meeting-{{ m.number }}">
    <div class="meeting-top">
      <span class="meeting-no">#{{ m.number }}</span>
      <time class="meeting-date" datetime="{{ md }}">{{ m.date | date: "%-d %B %Y" }}</time>
      {% if m.time %}<span class="meeting-time">{{ m.time }} {{ m.timezone | default: tz }}{% if m.duration %} · {{ m.duration }} min{% endif %}</span>{% endif %}
      <span class="badge badge-planned">Planned</span>
      {% if m.example %}<span class="badge badge-example" title="Placeholder entry — replace or delete">example</span>{% endif %}
    </div>

    <h3 class="meeting-title">{{ m.title }}</h3>

    {% if m.agenda %}
    <div class="agenda">
      <p class="agenda-label">Agenda</p>
      <ol class="agenda-list">
        {% for item in m.agenda %}<li>{{ item }}</li>{% endfor %}
      </ol>
    </div>
    {% else %}
    <p class="muted">Agenda to be published.</p>
    {% endif %}

    {% if m.summary %}<p class="meeting-summary">{{ m.summary }}</p>{% endif %}

    <p class="meeting-links">
      {% if m.join %}<a class="btn btn-ghost" href="{{ m.join }}">Join this meeting &#8599;</a>{% endif %}
      {% if mdecks.size > 0 %}<a class="btn btn-ghost" href="{{ '/presentations/' | relative_url }}#{{ mdecks.first.id }}">{{ mdecks.size }} presentation{% if mdecks.size != 1 %}s{% endif %} &#8594;</a>{% endif %}
    </p>
  </li>
{% endif %}
{% endfor %}
</ol>

## Previous <span class="group-count">{{ n_past }}</span>

{% if n_past == 0 %}
<p class="empty">No meetings have been held yet.</p>
{% endif %}

<ol class="meeting-list">
{% assign recent = all | reverse %}
{% for m in recent %}
{% assign md = m.date | date: "%Y-%m-%d" %}
{% if md < today %}
  {% assign mdecks = decks | where: "meeting", m.number %}
  <li class="meeting meeting-past" id="meeting-{{ m.number }}">
    <div class="meeting-top">
      <span class="meeting-no">#{{ m.number }}</span>
      <time class="meeting-date" datetime="{{ md }}">{{ m.date | date: "%-d %B %Y" }}</time>
      {% if m.recording %}<span class="badge badge-recording">Recording</span>
      {% elsif m.recording_members_only %}<span class="badge badge-recording" title="Shared with PKI Consortium members, not published here">Recording for members</span>
      {% elsif m.no_recording %}<span class="badge badge-norecording">Not recorded</span>
      {% else %}<span class="badge badge-pending">Recording to follow</span>{% endif %}
      {% if m.example %}<span class="badge badge-example" title="Placeholder entry — replace or delete">example</span>{% endif %}
    </div>

    <h3 class="meeting-title">{{ m.title }}</h3>

    {% if m.summary %}<p class="meeting-summary">{{ m.summary }}</p>{% endif %}

    {% if m.agenda %}
    <details class="agenda-past">
      <summary>What was on the agenda</summary>
      <ol class="agenda-list">
        {% for item in m.agenda %}<li>{{ item }}</li>{% endfor %}
      </ol>
    </details>
    {% endif %}

    {% if mdecks.size > 0 %}
    <div class="meeting-decks">
      <p class="agenda-label">Presented</p>
      <ul class="deck-inline">
        {% for p in mdecks %}
        <li>
          <a href="{{ '/presentations/' | relative_url }}#{{ p.id }}">{{ p.title }}</a>
          <span class="muted">— {{ p.presenter | join: ", " }}</span>
        </li>
        {% endfor %}
      </ul>
    </div>
    {% endif %}

    <p class="meeting-links">
      {% if m.recording %}<a class="btn btn-ghost" href="{{ m.recording }}">Watch the recording &#8599;</a>{% endif %}
      {% if m.minutes %}<a class="btn btn-ghost" href="{{ m.minutes }}">Minutes &#8599;</a>{% endif %}
      {% if mdecks.size > 0 %}<a class="btn btn-ghost" href="{{ '/presentations/' | relative_url }}#{{ mdecks.first.id }}">Presentations &#8594;</a>{% endif %}
    </p>
  </li>
{% endif %}
{% endfor %}
</ol>

<p class="muted note">
  <strong>For maintainers.</strong> Meetings are one data file,
  <a href="{{ site.repo.url }}/blob/main/docs/_data/meetings.yml"><code>docs/_data/meetings.yml</code></a>.
  A meeting moves from Upcoming to Previous on the first site build after its date, so publish
  the recording and the meeting moves itself. Field definitions and house rules are in
  <a href="{{ site.repo.url }}/blob/main/CONTRIBUTING-meetings.md">CONTRIBUTING-meetings.md</a>.
</p>
