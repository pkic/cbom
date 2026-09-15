(function () {
  'use strict';

  var results = document.getElementById('results');
  if (!results) return;               // the page renders no controls when empty

  var decks    = Array.prototype.slice.call(results.querySelectorAll('.deck'));
  var q        = document.getElementById('q');
  var groupSel = document.getElementById('groupby');
  var clearBtn = document.getElementById('clear');
  var count    = document.getElementById('count');
  var empty    = document.getElementById('empty');

  // Preserve the source order — newest first — so grouping is stable and reversible.
  decks.forEach(function (el, i) { el.dataset.order = i; });

  function matches(el) {
    var term = q.value.trim().toLowerCase();
    return !term || el.dataset.search.indexOf(term) !== -1;
  }

  function isFiltered() { return !!q.value.trim(); }

  function render() {
    var groupBy = groupSel.value;
    var visible = decks.filter(matches);

    Array.prototype.slice.call(results.querySelectorAll('.group-heading'))
      .forEach(function (h) { h.remove(); });

    decks.forEach(function (el) { el.hidden = true; });

    // Group, preserving source order within each group. The data attribute already
    // holds the display text, so no label lookup is needed.
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
      h.appendChild(document.createTextNode(key));
      var c = document.createElement('span');
      c.className = 'group-count';
      c.textContent = items.length;
      h.appendChild(document.createTextNode(' '));
      h.appendChild(c);
      results.appendChild(h);
      items.forEach(function (el) { el.hidden = false; results.appendChild(el); });
    });

    count.textContent = isFiltered()
      ? visible.length + ' of ' + decks.length + ' presentations shown'
      : decks.length + (decks.length === 1 ? ' presentation' : ' presentations');
    empty.hidden = visible.length !== 0;
    clearBtn.hidden = !isFiltered();
  }

  clearBtn.addEventListener('click', function () {
    q.value = '';
    render();
    q.focus();
  });

  q.addEventListener('input', render);
  groupSel.addEventListener('change', render);

  // A link to #<id> only reaches the card if its group is rendered, which it is on
  // first paint. Scroll to it after grouping so deep links from the meetings page land.
  render();
  if (window.location.hash) {
    var target = document.getElementById(window.location.hash.slice(1));
    if (target) target.scrollIntoView();
  }
})();
