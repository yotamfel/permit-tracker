export const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

// True if `month` (1-12) falls within the [start, end] season, handling a
// season that wraps the new year (e.g. start=11, end=3 covers Nov-Mar).
export function monthInSeason(month, start, end) {
  if (start == null || end == null) return false;
  if (start <= end) return month >= start && month <= end;
  return month >= start || month <= end;
}
