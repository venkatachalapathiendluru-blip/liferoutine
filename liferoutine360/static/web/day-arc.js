// Day Arc — positions the "now" marker along the top gradient by time of day.
(function () {
  const arc = document.querySelector('.day-arc');
  if (!arc) return;
  const dot = document.createElement('span');
  dot.className = 'now-dot';
  dot.setAttribute('aria-hidden', 'true');
  arc.appendChild(dot);

  function place() {
    const now = new Date();
    const minutes = now.getHours() * 60 + now.getMinutes();
    const pct = (minutes / 1440) * 100;
    dot.style.left = pct.toFixed(2) + '%';
    arc.title = 'Your day: ' + now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  place();
  setInterval(place, 60 * 1000);
})();
