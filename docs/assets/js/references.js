(function () {
  'use strict';

  var results = document.getElementById('results');
  var refs    = Array.prototype.slice.call(results.querySelectorAll('.ref'));
  var q       = document.getElementById('q');
  var juris   = document.getElementById('jurisdiction');
  var groupSel= document.getElementById('groupby');
  var clearBtn= document.getElementById('clear');
  var count   = document.getElementById('count');
  var empty   = document.getElementById('empty');
  var labels  = window.CBOM_LABELS || { category: {}, jurisdiction: {}, status: {} };

  // Preserve the source order so grouping is stable and reversible.
  refs.forEach(function (el, i) { el.dataset.order = i; });

  var active = { category: [], status: [] };

  function matches(el) {
    for (var facet in active) {
      var chosen = active[facet];
      if (chosen.length && chosen.indexOf(el.dataset[facet]) === -1) return false;
    }
    if (juris.value && el.dataset.jurisdiction !== juris.value) return false;
    var term = q.value.trim().toLowerCase();
    if (term && el.dataset.search.indexOf(term) === -1) return false;
    return true;
  }

  function isFiltered() {
    return active.category.length || active.status.length ||
           juris.value || q.value.trim();
  }

  function render() {
    var groupBy = groupSel.value;
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
      var items = groups[key].sort(function (a, b) {
        return a.dataset.order - b.dataset.order;
      });
      var h = document.createElement('h2');
      h.className = 'group-heading';
      h.innerHTML = ((labels[groupBy] && labels[groupBy][key]) || key) +
                    ' <span class="group-count">' + items.length + '</span>';
      results.appendChild(h);
      items.forEach(function (el) { el.hidden = false; results.appendChild(el); });
    });

    count.textContent = isFiltered()
      ? visible.length + ' of ' + refs.length + ' references shown'
      : refs.length + ' references';
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
    active = { category: [], status: [] };
    q.value = '';
    juris.value = '';
    document.querySelectorAll('.chip[data-facet]').forEach(function (c) {
      c.classList.remove('is-on');
      c.setAttribute('aria-pressed', 'false');
    });
    render();
    q.focus();
  });

  q.addEventListener('input', render);
  juris.addEventListener('change', render);
  groupSel.addEventListener('change', render);

  render();
})();
