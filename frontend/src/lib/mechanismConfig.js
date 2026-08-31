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
      return `Opens every year on ${formatMonthDay(config.typical_release_date)} at ${config.release_time} (${config.timezone}).`;
    case "weekly_release":
      return `New availability releases every ${capitalize(config.release_weekday)} at ${config.release_time} (${config.timezone}), roughly ${config.weeks_ahead} weeks ahead.`;
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
