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
  // PRINTED dates win when the printed ad runs longer than Wed-Tue (Thanksgiving ad 2026: Nov 18-26).
  const PRINTED = { start: new Date(2026, 10, 18), end: new Date(2026, 10, 26, 23, 59, 59) };
  let wed = new Date(now);
  wed.setDate(now.getDate() - ((now.getDay() + 4) % 7));
  let tue = new Date(wed);
  tue.setDate(wed.getDate() + 6);
  if (now >= PRINTED.start && now <= PRINTED.end) { wed = PRINTED.start; tue = PRINTED.end; }
  const fmt = d => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const week = `${fmt(wed)} – ${fmt(tue)}`;
  const inPrinted = now >= PRINTED.start && now <= PRINTED.end;
  const sentence = inPrinted ? `Wed ${fmt(wed)} through ${fmt(tue)}` : `Wed ${fmt(wed)} through Tue ${fmt(tue)}`;
  ['utilWeek', 'pageWeek'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = sentence; });
  const hw = document.getElementById('heroWeek'); if (hw) hw.textContent = week;

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
