// Rooms: the room at the top of a main page spreads over the page (rooms.js rWall; docs/plans/2026-11-11-the-climb.md §8).
// Runs in the page (check.js: `bad` in scope). On every page that opens with a room the wall lies behind the whole page:
// it is there, it carries the painted tile, it is as wide as the window and reaches the top of the page, and it does not
// make the page scroll sideways. The home page (its own sky) and a detail page have no wall.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), go = async h => { location.hash = h; await wait(60); render(); await wait(350); };
  for (const h of ['#home', '#gear', '#bosses', '#build', '#mechanics', '#changes']) { await go(h);
    const w = document.querySelector('#main>.rwall'), r = document.querySelector('#main .room3');
    if (!r) { bad.push(`rooms ${h}: the page has no room`); continue; }
    if (!w) { bad.push(`rooms ${h}: the room's wall does not go on behind the page`); continue; }
    const b = w.getBoundingClientRect(), de = document.documentElement;
    if (!/^url\("data:image\/png/.test(getComputedStyle(w).backgroundImage)) bad.push(`rooms ${h}: the wall has no painted tile`);
    if (Math.abs(b.left) > 1 || Math.abs(b.width - de.clientWidth) > 1 || b.top + scrollY > 1) bad.push(`rooms ${h}: the wall is ${Math.round(b.width)} px wide from ${Math.round(b.left)}, top ${Math.round(b.top + scrollY)} (window ${de.clientWidth})`);
    if (de.scrollWidth > de.clientWidth) bad.push(`rooms ${h}: the page scrolls sideways (${de.scrollWidth} > ${de.clientWidth})`); }
  for (const h of ['#', '#i5']) { await go(h); if (document.querySelector('#main>.rwall')) bad.push(`rooms ${h || 'home'}: a wall on a page without a room`); } }
