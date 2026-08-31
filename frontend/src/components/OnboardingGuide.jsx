import { useState } from "react";
import { useOnboarding } from "../lib/OnboardingContext";

const STEPS = [
  {
    title: "Search destinations",
    text: "Find the trek, park, dive, or event you're after - filter by country or category.",
    illustration: <SearchMockup />,
  },
  {
    title: "See what's involved, before you buy",
    text: "Every destination page shows a free description of the place and how competitive it is - no purchase needed to read that part.",
    illustration: <DetailMockup />,
  },
  {
    title: "Unlock your game plan",
    text: "One quick unlock reveals exactly how the permit works, plus the full checklist and the exact steps, dates, and documents you need.",
    illustration: <LockedMockup />,
  },
  {
    title: "Check off what you've done",
    text: "Track your prep with a checklist you can tick off, and jump straight to the official application when you're ready.",
    illustration: <ChecklistMockup />,
  },
  {
    title: "Never miss the opening",
    text: "Set an alert and we'll email you before the application window opens - from two weeks out down to 30 minutes.",
    illustration: <AlertMockup />,
  },
];

export default function OnboardingGuide() {
  const { isOpen, closeGuide } = useOnboarding();
  const [step, setStep] = useState(0);

  if (!isOpen) return null;

  const isLast = step === STEPS.length - 1;
  const current = STEPS[step];

  const handleClose = () => {
    setStep(0);
    closeGuide();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl dark:bg-stone-900">
        <div className="flex items-start justify-between">
          <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100">{current.title}</h2>
          <button
            onClick={handleClose}
            aria-label="Close"
            className="text-stone-400 hover:text-stone-600 dark:hover:text-stone-200"
          >
            ✕
          </button>
        </div>

        <div className="mt-4">{current.illustration}</div>

        <p className="mt-4 text-sm text-stone-600 dark:text-stone-400">{current.text}</p>

        <div className="mt-6 flex items-center justify-between">
          <div className="flex gap-1.5">
            {STEPS.map((_, i) => (
              <span
                key={i}
                className={`h-1.5 w-1.5 rounded-full ${
                  i === step ? "bg-amber-600" : "bg-stone-200 dark:bg-stone-700"
                }`}
              />
            ))}
          </div>
          <div className="flex gap-2">
            {step > 0 && (
              <button
                onClick={() => setStep((s) => s - 1)}
                className="rounded-full border border-stone-300 px-4 py-1.5 text-sm text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
              >
                Back
              </button>
            )}
            {!isLast ? (
              <>
                <button
                  onClick={handleClose}
                  className="rounded-full px-4 py-1.5 text-sm text-stone-500 hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  Skip
                </button>
                <button
                  onClick={() => setStep((s) => s + 1)}
                  className="rounded-full bg-amber-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-amber-700"
                >
                  Next
                </button>
              </>
            ) : (
              <button
                onClick={handleClose}
                className="rounded-full bg-amber-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-amber-700"
              >
                Get started
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MockCard({ children, className = "" }) {
  return (
    <div className={`rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-800/50 ${className}`}>
      {children}
    </div>
  );
}

function SearchMockup() {
  const examples = [
    { emoji: "🥾", name: "Half Dome Cables", country: "USA" },
    { emoji: "🏞️", name: "Torres del Paine", country: "Chile" },
    { emoji: "🤿", name: "Blue Hole", country: "Belize" },
  ];
  return (
    <MockCard>
      <div className="flex items-center gap-2 rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-sm text-stone-400 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-500">
        <span aria-hidden="true">🔎</span>
        Search destinations...
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        {examples.map((ex) => (
          <div key={ex.name} className="rounded-lg bg-white p-2 text-center dark:bg-stone-900">
            <span aria-hidden="true">{ex.emoji}</span>
            <div className="mt-1 text-[11px] font-medium leading-tight text-stone-800 dark:text-stone-200">{ex.name}</div>
            <div className="text-[10px] text-stone-500 dark:text-stone-400">{ex.country}</div>
          </div>
        ))}
      </div>
    </MockCard>
  );
}

function DetailMockup() {
  return (
    <MockCard>
      <span className="text-[10px] font-medium uppercase tracking-wide text-amber-700 dark:text-amber-400">Trek</span>
      <h4 className="text-sm font-bold text-stone-900 dark:text-stone-100">Half Dome Cables Route</h4>
      <p className="text-[11px] text-stone-500 dark:text-stone-400">Yosemite National Park, USA</p>
      <p className="mt-1.5 text-[11px] leading-snug text-stone-600 dark:text-stone-300">
        A steep granite dome with a cable-assisted final pitch and sweeping valley views - one of Yosemite's
        signature hikes, and one of its hardest permits to land.
      </p>
      <div className="mt-2">
        <span className="rounded-full bg-rose-100 px-2 py-0.5 text-[10px] font-medium text-rose-800 dark:bg-rose-900/40 dark:text-rose-300">
          Very high competitiveness
        </span>
      </div>
    </MockCard>
  );
}

function LockedMockup() {
  return (
    <MockCard className="relative overflow-hidden">
      <div className="space-y-1.5 text-[11px] text-stone-600 blur-[3px] dark:text-stone-300">
        <p>☐ Valid wilderness permit</p>
        <p>☐ Cable route dates: Jun-Oct only</p>
        <p>☐ Daily lottery entry (pre-season)</p>
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-white/50 dark:bg-stone-900/50">
        <span className="rounded-full bg-amber-600 px-4 py-1.5 text-xs font-semibold text-white shadow-sm">
          Unlock for $4.99
        </span>
      </div>
    </MockCard>
  );
}

function ChecklistMockup() {
  return (
    <MockCard>
      {[
        { text: "Valid photo ID", done: true },
        { text: "Printed permit confirmation", done: true },
        { text: "Rain jacket & gloves (cables get slick)", done: false },
      ].map((item) => (
        <div key={item.text} className="flex items-center gap-2 py-1">
          <span
            className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border text-[10px] ${
              item.done ? "border-amber-600 bg-amber-600 text-white" : "border-stone-300 dark:border-stone-600"
            }`}
          >
            {item.done ? "✓" : ""}
          </span>
          <span
            className={`text-[11px] ${
              item.done
                ? "text-stone-400 line-through dark:text-stone-500"
                : "text-stone-700 dark:text-stone-300"
            }`}
          >
            {item.text}
          </span>
        </div>
      ))}
      <div className="mt-2 inline-block rounded-full bg-emerald-600 px-3 py-1 text-[10px] font-semibold text-white">
        Continue to official site ↗
      </div>
    </MockCard>
  );
}

function AlertMockup() {
  return (
    <MockCard>
      <div className="flex items-center gap-2 text-[11px] font-medium text-stone-700 dark:text-stone-300">
        <span aria-hidden="true">🔔</span>
        Notify me before it opens
      </div>
      <div className="mt-2 rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-[10px] text-stone-600 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300">
        1 week before ▾
      </div>
      <div className="mt-2 inline-block rounded-full bg-amber-600 px-3 py-1 text-[10px] font-semibold text-white">
        Set alert
      </div>
    </MockCard>
  );
}
