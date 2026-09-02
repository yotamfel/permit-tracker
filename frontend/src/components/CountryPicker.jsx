import { useState } from "react";
import { COUNTRIES } from "../lib/countries";

// Type-to-filter country picker - typing narrows the list to countries whose
// name starts with what's typed (prefix match, not substring), matching the
// admin search convention used elsewhere in the app.
export default function CountryPicker({ value, onChange, placeholder = "Country (optional)" }) {
  const [query, setQuery] = useState(value || "");
  const [open, setOpen] = useState(false);

  const filtered = query
    ? COUNTRIES.filter((c) => c.toLowerCase().startsWith(query.toLowerCase()))
    : COUNTRIES;

  const select = (country) => {
    setQuery(country);
    onChange(country);
    setOpen(false);
  };

  return (
    <div className="relative">
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          onChange("");
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={placeholder}
        className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
      />
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute z-20 mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-stone-200 bg-white shadow-lg dark:border-stone-800 dark:bg-stone-900">
            {filtered.length === 0 ? (
              <div className="px-2 py-1.5 text-sm text-stone-500 dark:text-stone-400">No match</div>
            ) : (
              filtered.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => select(c)}
                  className="block w-full px-2 py-1.5 text-left text-sm hover:bg-stone-100 dark:hover:bg-stone-800"
                >
                  {c}
                </button>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}
