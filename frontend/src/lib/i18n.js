import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "../locales/en/common.json";

// English-only for now (multilingual support paused at the user's request).
// The other 5 locales' translated UI strings are archived at
// /future-i18n/frontend-locales/{he,de,fr,es,pt-BR}/common.json - to resume,
// move them back into src/locales/, re-add them to the `resources` map below,
// and un-hide the language switcher in components/Header.jsx.
export const SUPPORTED_LOCALES = ["en"];

i18n.use(initReactI18next).init({
  resources: {
    en: { common: en },
  },
  lng: "en",
  fallbackLng: "en",
  ns: ["common"],
  defaultNS: "common",
  interpolation: { escapeValue: false },
});

export default i18n;
