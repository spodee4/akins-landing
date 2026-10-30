// Shared page behavior: mobile menu, ad-week dates, open-now chips.
(function () {
  const toggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('open');
      navLinks.classList.toggle('open');
    });
  }

  // Ad week runs Wednesday through Tuesday (local time), same rule as the weekly ad page.
  const now = new Date();
  const wed = new Date(now);
  wed.setDate(now.getDate() - ((now.getDay() + 4) % 7));
  const tue = new Date(wed);
  tue.setDate(wed.getDate() + 6);
  const fmt = d => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const week = `${fmt(wed)} – ${fmt(tue)}`;
  ['utilWeek', 'heroWeek'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = week; });

  // Open-now chip per store card, judged in Pacific time (all five stores are in Washington).
  const parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' }).formatToParts(now);
  const get = t => Number(parts.find(p => p.type === t).value);
  const mins = get('hour') * 60 + get('minute');
  const toMins = s => { const [h, m] = s.split(':').map(Number); return h * 60 + m; };
  document.querySelectorAll('.store-card[data-open]').forEach(card => {
    const chip = card.querySelector('.chip-open');
    if (!chip) return;
    const open = mins >= toMins(card.dataset.open) && mins < toMins(card.dataset.close);
    chip.textContent = open ? 'Open now' : 'Closed';
    chip.classList.add(open ? 'yes' : 'no');
  });
})();
