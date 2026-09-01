// A little variety instead of just the alphabetically-first few: prefer
// higher-competitiveness destinations (the ones people are most likely to
// search for) and spread across categories rather than piling up one type.
export function pickFeatured(destinations, count = 6) {
  const seenCategories = new Set();
  const ranked = [...destinations].sort((a, b) => {
    const order = { very_high: 0, high: 1, medium: 2, low: 3 };
    return (order[a.competitiveness_level] ?? 4) - (order[b.competitiveness_level] ?? 4);
  });

  const picked = [];
  for (const d of ranked) {
    if (picked.length >= count) break;
    if (seenCategories.has(d.category)) continue;
    seenCategories.add(d.category);
    picked.push(d);
  }
  if (picked.length < count) {
    for (const d of ranked) {
      if (picked.length >= count) break;
      if (!picked.includes(d)) picked.push(d);
    }
  }
  return picked;
}
