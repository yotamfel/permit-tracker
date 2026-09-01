const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function formatMonthDay(md) {
  if (!md) return "";
  const [month, day] = md.split("-").map(Number);
  return `${MONTH_NAMES[month - 1]} ${day}`;
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// How many minutes `timeZone`'s local clock is ahead of UTC at the given
// instant (handles DST correctly since it asks the real Intl formatter for
// that specific date, not a fixed offset).
function timeZoneOffsetMinutes(date, timeZone) {
  const dtf = new Intl.DateTimeFormat("en-US", {
    timeZone,
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  const parts = dtf.formatToParts(date).reduce((acc, p) => {
    acc[p.type] = p.value;
    return acc;
  }, {});
  const asUTC = Date.UTC(
    Number(parts.year),
    Number(parts.month) - 1,
    Number(parts.day),
    parts.hour === "24" ? 0 : Number(parts.hour),
    Number(parts.minute),
    Number(parts.second)
  );
  return (asUTC - date.getTime()) / 60000;
}

// Renders a release time as both the destination's local time and its UTC
// equivalent (e.g. "09:00 (Australia/Hobart) / 23:00 UTC the day before"),
// so a visitor anywhere in the world knows exactly when to be online -
// `monthDay` ("MM-DD") anchors which date's DST rules apply.
function formatTimeWithUTC(monthDay, timeStr, timezone) {
  if (!timeStr || !timezone) return timeStr || "";
  const [hour, minute] = timeStr.split(":").map(Number);
  const now = new Date();
  const [month, day] = monthDay ? monthDay.split("-").map(Number) : [now.getMonth() + 1, now.getDate()];

  let guess = new Date(Date.UTC(now.getFullYear(), month - 1, day, hour, minute));
  const offsetMin = timeZoneOffsetMinutes(guess, timezone);
  const utcDate = new Date(guess.getTime() - offsetMin * 60000);

  const utcHH = String(utcDate.getUTCHours()).padStart(2, "0");
  const utcMM = String(utcDate.getUTCMinutes()).padStart(2, "0");
  const dayShift =
    utcDate.getUTCDate() !== guess.getUTCDate() ? (utcDate.getUTCDate() < guess.getUTCDate() ? " (the day before)" : " (the day after)") : "";

  return `${timeStr} (${timezone}) / ${utcHH}:${utcMM} UTC${dayShift}`;
}

// Turns the raw mechanism_config JSON into a plain-language sentence, keyed
// by mechanism_type - this is what unlocked users see instead of raw JSON.
export function formatMechanismConfig(mechanismType, config) {
  if (!config) return null;
  switch (mechanismType) {
    case "fixed_daily_quota":
      return `Daily quota: ${config.daily_quota} permits/day. Booking typically opens ${config.booking_opens_days_before} days before your date.`;
    case "lottery": {
      const main = `Applications open ${formatMonthDay(config.application_window_start)} - ${formatMonthDay(
        config.application_window_end
      )} each year, with results announced around ${formatMonthDay(config.results_date)}.`;
      if (config.registration_window) {
        return `Registration opens ${formatMonthDay(config.registration_window.start)} - ${formatMonthDay(
          config.registration_window.end
        )}, before the lottery itself. ${main}`;
      }
      return main;
    }
    case "rolling_window":
      return `Booking opens ${config.days_before_travel_date} days before your travel date.`;
    case "fixed_annual_date":
      return `Opens every year on ${formatMonthDay(config.typical_release_date)} at ${formatTimeWithUTC(config.typical_release_date, config.release_time, config.timezone)}.`;
    case "weekly_release":
      return `New availability releases every ${capitalize(config.release_weekday)} at ${formatTimeWithUTC(null, config.release_time, config.timezone)}, roughly ${config.weeks_ahead} weeks ahead.`;
    case "guided_tour_only":
      return config.note || "No self-service release date - depends on tour operator availability.";
    case "single_operator_annual_quota":
      return `Operated exclusively by ${config.operator_name}. Annual quota: ${config.annual_quota}. Typical booking lead time: ${config.typical_booking_lead_time_months} months.`;
    case "first_come_first_served":
      return `Typical booking lead time: ${config.typical_booking_lead_time_months} months ahead.`;
    default:
      return null;
  }
}

// Same data as formatMechanismConfig, but as separate stat lines instead of
// one blended sentence - used on the free preview where each number needs
// to stand out on its own rather than get lost inside a paragraph.
export function getMechanismStats(mechanismType, config) {
  if (!config) return [];
  switch (mechanismType) {
    case "fixed_daily_quota":
      return [`Daily quota: ${config.daily_quota} permits/day`, `Booking opens: ${config.booking_opens_days_before} days before your date`];
    case "lottery": {
      const stats = [];
      if (config.registration_window) {
        stats.push(`Registration window: ${formatMonthDay(config.registration_window.start)} - ${formatMonthDay(config.registration_window.end)}`);
      }
      stats.push(`Application window: ${formatMonthDay(config.application_window_start)} - ${formatMonthDay(config.application_window_end)}`);
      stats.push(`Results announced: around ${formatMonthDay(config.results_date)}`);
      return stats;
    }
    case "rolling_window":
      return [`Booking opens: ${config.days_before_travel_date} days before your travel date`];
    case "fixed_annual_date":
      return [
        `Opens every year: ${formatMonthDay(config.typical_release_date)}`,
        `Release time: ${formatTimeWithUTC(config.typical_release_date, config.release_time, config.timezone)}`,
      ];
    case "weekly_release":
      return [
        `Releases every ${capitalize(config.release_weekday)} at ${formatTimeWithUTC(null, config.release_time, config.timezone)}`,
        `Availability window: roughly ${config.weeks_ahead} weeks ahead`,
      ];
    case "guided_tour_only":
      return [config.note || "No self-service release date - depends on tour operator availability"];
    case "single_operator_annual_quota":
      return [`Operator: ${config.operator_name}`, `Annual quota: ${config.annual_quota}`, `Typical booking lead time: ${config.typical_booking_lead_time_months} months`];
    case "first_come_first_served":
      return [`Typical booking lead time: ${config.typical_booking_lead_time_months} months ahead`];
    default:
      return [];
  }
}
