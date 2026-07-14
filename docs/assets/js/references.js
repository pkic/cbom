(function () {
  'use strict';

  var results = document.getElementById('results');
  var refs    = Array.prototype.slice.call(results.querySelectorAll('.ref'));
  var q       = document.getElementById('q');
  var count   = document.getElementById('count');
  var empty   = document.getElementById('empty');
  var labels  = window.CBOM_LABELS || { category: {}, jurisdiction: {} };

  // Preserve the source order so grouping is stable and reversible.
  refs.forEach(function (el, i) { el.dataset.order = i; });

  var active = { category: [], status: [], jurisdiction: [] };
  var groupBy = 'category';

  function matches(el) {
    for (var facet in active) {
      var chosen = active[facet];
      if (chosen.length && chosen.indexOf(el.dataset[facet]) === -1) return false;
    }
    var term = q.value.trim().toLowerCase();
    if (term && el.dataset.search.indexOf(term) === -1) return false;
    return true;
  }

  function render() {
    var visible = refs.filter(matches);

    // Clear existing group headings before regrouping.
    Array.prototype.slice.call(results.querySelectorAll('.group-heading'))
      .forEach(function (h) { h.remove(); });

    refs.forEach(function (el) { el.hidden = true; });

    // Group, preserving source order within each group.
    var groups = {};
    var order = [];
    visible.forEach(function (el) {
      var key = el.dataset[groupBy];
      if (!groups[key]) { groups[key] = []; order.push(key); }
      groups[key].push(el);
    });

    order.forEach(function (key) {
      var h = document.createElement('h2');
      h.className = 'group-heading';
      h.textContent = (labels[groupBy] && labels[groupBy][key]) || key;
      results.appendChild(h);
      groups[key]
        .sort(function (a, b) { return a.dataset.order - b.dataset.order; })
        .forEach(function (el) { el.hidden = false; results.appendChild(el); });
    });

    count.textContent = visible.length + ' of ' + refs.length + ' shown';
    empty.hidden = visible.length !== 0;
  }

  document.querySelectorAll('.chip[data-facet]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var facet = chip.dataset.facet;
      var value = chip.dataset.value;
      var at = active[facet].indexOf(value);
      if (at === -1) { active[facet].push(value); chip.classList.add('is-on'); }
      else { active[facet].splice(at, 1); chip.classList.remove('is-on'); }
      render();
    });
  });

  document.querySelectorAll('.chip[data-group]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      document.querySelectorAll('.chip[data-group]').forEach(function (c) {
        c.classList.remove('is-on');
      });
      chip.classList.add('is-on');
      groupBy = chip.dataset.group;
      render();
    });
  });

  document.getElementById('clear').addEventListener('click', function () {
    active = { category: [], status: [], jurisdiction: [] };
    q.value = '';
    document.querySelectorAll('.chip[data-facet]').forEach(function (c) {
      c.classList.remove('is-on');
    });
    render();
  });

  q.addEventListener('input', render);

  render();
})();
