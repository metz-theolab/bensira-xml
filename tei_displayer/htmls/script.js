window.addEventListener('DOMContentLoaded', function() {
  const spacing = 5;
  const marginHeight = 18;

  // Regroupe les marges par data-line
  const marginsByLine = {};
  document.querySelectorAll('span.margin[data-line]').forEach(function(margin) {
    const line = margin.getAttribute('data-line');
    if (!marginsByLine[line]) marginsByLine[line] = [];
    marginsByLine[line].push(margin);
  });

  Object.keys(marginsByLine).forEach(function(line) {
    // Trouve le <p class="verse"> qui contient le <sup class="line"> avec ce numéro
    let refP = null;
    document.querySelectorAll('p.verse').forEach(function(p) {
      const sup = p.querySelector('sup.line');
      if (sup && sup.textContent.replace(/\D/g, '') === line) refP = p;
    });
    if (refP) {
      const pRect = refP.getBoundingClientRect();
      const bodyRect = document.body.getBoundingClientRect();
      let top = pRect.top - bodyRect.top;
      marginsByLine[line].forEach(function(margin, idx) {
        margin.style.position = "absolute";
        margin.style.top = (top + idx * (marginHeight + spacing)) + "px";
      });
    }
  });
});