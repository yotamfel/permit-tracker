// Tracks, per admin nav tab, how many list items are new since the admin
// last opened that tab - a small "N new" badge in the sidebar, distinct from
// the tab's total count. Purely a per-browser convenience (localStorage) -
// there's only one admin using one browser, so no need for server-side state.
const KEY_PREFIX = "admin_last_seen_";

function readLastSeen(tabKey) {
  try {
    const raw = localStorage.getItem(KEY_PREFIX + tabKey);
    return raw ? new Date(raw) : null;
  } catch {
    return null;
  }
}

export function markSeen(tabKey) {
  try {
    localStorage.setItem(KEY_PREFIX + tabKey, new Date().toISOString());
  } catch {
    // ignore (private browsing, storage disabled, etc.) - badge just won't persist
  }
}

// Counts items newer than the last-seen timestamp for this tab. The very
// first time a tab is checked (no last-seen timestamp recorded yet), this
// establishes "now" as the baseline and returns 0 - otherwise every
// pre-existing item would falsely show as new the first time this feature
// runs for a tab.
export function countUnseen(tabKey, items, getTimestamp) {
  let lastSeen = readLastSeen(tabKey);
  if (!lastSeen) {
    markSeen(tabKey);
    return 0;
  }
  return items.filter((item) => {
    const ts = getTimestamp(item);
    return ts && new Date(ts) > lastSeen;
  }).length;
}

// Same idea as countUnseen, for tabs with no natural per-item timestamp (e.g.
// aggregated feedback stats) - tracks a running total instead of a date, and
// "unseen" is however much that total grew since it was last checked.
const TOTAL_KEY_PREFIX = "admin_last_seen_total_";

export function countUnseenByTotal(tabKey, currentTotal) {
  let raw;
  try {
    raw = localStorage.getItem(TOTAL_KEY_PREFIX + tabKey);
  } catch {
    raw = null;
  }
  if (raw === null) {
    markSeenTotal(tabKey, currentTotal);
    return 0;
  }
  return Math.max(0, currentTotal - Number(raw));
}

export function markSeenTotal(tabKey, total) {
  try {
    localStorage.setItem(TOTAL_KEY_PREFIX + tabKey, String(total));
  } catch {
    // ignore
  }
}
