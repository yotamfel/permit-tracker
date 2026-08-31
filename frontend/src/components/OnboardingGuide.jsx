import { useState } from "react";
import { useOnboarding } from "../lib/OnboardingContext";

const STEPS = [
  {
    title: "Search destinations",
    text: "Find the trek, park, dive, or event you're after - filter by country, category, or how competitive it is.",
    illustration: <SearchMockup />,
  },
  {
    title: "See what's involved, before you buy",
    text: "Every destination page explains how the permit works and how competitive it is, in plain language - free to read, no purchase needed.",
    illustration: <DetailMockup />,
  },
  {
    title: "Unlock your game plan",
    text: "One quick unlock reveals the full checklist and the exact steps, dates, and documents you need.",
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

function Bar({ w = "100%", className = "" }) {
  return <div className={`h-2 rounded bg-stone-200 dark:bg-stone-700 ${className}`} style={{ width: w }} />;
}

function SearchMockup() {
  return (
    <MockCard>
      <div className="flex items-center gap-2 rounded-lg border border-stone-300 bg-white px-2 py-1.5 dark:border-stone-700 dark:bg-stone-900">
        <span aria-hidden="true">🔎</span>
        <Bar w="60%" />
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2">
        {["🥾", "🏞️", "🤿"].map((emoji, i) => (
          <div key={i} className="rounded-lg bg-white p-2 dark:bg-stone-900">
            <span aria-hidden="true">{emoji}</span>
            <Bar w="80%" className="mt-2" />
            <Bar w="50%" className="mt-1" />
          </div>
        ))}
      </div>
    </MockCard>
  );
}

function DetailMockup() {
  return (
    <MockCard>
      <Bar w="30%" className="bg-amber-200 dark:bg-amber-800" />
      <Bar w="70%" className="mt-2 h-3" />
      <Bar w="90%" className="mt-2" />
      <Bar w="85%" className="mt-1.5" />
      <div className="mt-3 flex items-center gap-2">
        <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
          Medium competitiveness
        </span>
      </div>
    </MockCard>
  );
}

function LockedMockup() {
  return (
    <MockCard className="relative overflow-hidden">
      <div className="space-y-2 blur-sm">
        <Bar w="90%" />
        <Bar w="75%" />
        <Bar w="82%" />
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-white/40 dark:bg-stone-900/40">
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
      {["Valid passport", "Permit application form", "Travel insurance"].map((text, i) => (
        <div key={text} className="flex items-center gap-2 py-1">
          <span
            className={`flex h-4 w-4 items-center justify-center rounded border text-[10px] ${
              i < 2
                ? "border-amber-600 bg-amber-600 text-white"
                : "border-stone-300 dark:border-stone-600"
            }`}
          >
            {i < 2 ? "✓" : ""}
          </span>
          <Bar w={i === 0 ? "50%" : i === 1 ? "70%" : "55%"} />
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
      <div className="flex items-center gap-2">
        <span aria-hidden="true">🔔</span>
        <Bar w="40%" />
      </div>
      <div className="mt-2 rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-[10px] text-stone-500 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-400">
        1 week before ▾
      </div>
      <div className="mt-2 inline-block rounded-full bg-amber-600 px-3 py-1 text-[10px] font-semibold text-white">
        Set alert
      </div>
    </MockCard>
  );
}
