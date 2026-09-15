(function () {
  'use strict';

  var results = document.getElementById('results');
  if (!results) return;               // the page renders no controls when empty

  var tools    = Array.prototype.slice.call(results.querySelectorAll('.tool'));
  var q        = document.getElementById('q');
  var groupSel = document.getElementById('groupby');
  var clearBtn = document.getElementById('clear');
  var count    = document.getElementById('count');
  var empty    = document.getElementById('empty');
  var labels   = window.CBOM_TOOL_LABELS || { primary: {}, licensing: {}, status: {} };

  // Preserve the source order — alphabetical — so grouping is stable and reversible.
  tools.forEach(function (el, i) { el.dataset.order = i; });

  // A tool does several things, so data-function holds a space-separated list and a
  // function chip matches any tool that lists it. Chips within one facet are OR'd;
  // facets are AND'd, as on the reference register.
  var active = { function: [], licensing: [] };

  function matches(el) {
    for (var facet in active) {
      var chosen = active[facet];
      if (!chosen.length) continue;
      var have = el.dataset[facet].split(' ');
      if (!chosen.some(function (v) { return have.indexOf(v) !== -1; })) return false;
    }
    var term = q.value.trim().toLowerCase();
    return !term || el.dataset.search.indexOf(term) !== -1;
  }

  function isFiltered() {
    return active.function.length || active.licensing.length || q.value.trim();
  }

  function render() {
    var groupBy = groupSel.value;
    var visible = tools.filter(matches);

    Array.prototype.slice.call(results.querySelectorAll('.group-heading'))
      .forEach(function (h) { h.remove(); });

    tools.forEach(function (el) { el.hidden = true; });

    var groups = {};
    var order = [];
    visible.forEach(function (el) {
      var key = el.dataset[groupBy];
      if (!groups[key]) { groups[key] = []; order.push(key); }
      groups[key].push(el);
    });

    // Groups follow the label order in _config.yml, not first appearance, so
    // "Generates" comes before "Consumes" however the names happen to sort.
    var ranked = Object.keys(labels[groupBy] || {});
    order.sort(function (a, b) { return ranked.indexOf(a) - ranked.indexOf(b); });

    order.forEach(function (key) {
      var items = groups[key].sort(function (a, b) {
        return a.dataset.order - b.dataset.order;
      });
      var h = document.createElement('h2');
      h.className = 'group-heading';
      h.appendChild(document.createTextNode((labels[groupBy] && labels[groupBy][key]) || key));
      var c = document.createElement('span');
      c.className = 'group-count';
      c.textContent = items.length;
      h.appendChild(document.createTextNode(' '));
      h.appendChild(c);
      results.appendChild(h);
      items.forEach(function (el) { el.hidden = false; results.appendChild(el); });
    });

    count.textContent = isFiltered()
      ? visible.length + ' of ' + tools.length + ' tools shown'
      : tools.length + (tools.length === 1 ? ' tool' : ' tools');
    empty.hidden = visible.length !== 0;
    clearBtn.hidden = !isFiltered();
  }

  document.querySelectorAll('.chip[data-facet]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var facet = chip.dataset.facet;
      var value = chip.dataset.value;
      var at = active[facet].indexOf(value);
      if (at === -1) { active[facet].push(value); chip.classList.add('is-on'); }
      else { active[facet].splice(at, 1); chip.classList.remove('is-on'); }
      chip.setAttribute('aria-pressed', at === -1 ? 'true' : 'false');
      render();
    });
    chip.setAttribute('aria-pressed', 'false');
  });

  clearBtn.addEventListener('click', function () {
    active = { function: [], licensing: [] };
    q.value = '';
    document.querySelectorAll('.chip[data-facet]').forEach(function (c) {
      c.classList.remove('is-on');
      c.setAttribute('aria-pressed', 'false');
    });
    render();
    q.focus();
  });

  q.addEventListener('input', render);
  groupSel.addEventListener('change', render);

  render();
  if (window.location.hash) {
    var target = document.getElementById(window.location.hash.slice(1));
    if (target) target.scrollIntoView();
  }
})();
