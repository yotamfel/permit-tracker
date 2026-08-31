import { createContext, useContext, useState } from "react";

const OnboardingContext = createContext(null);
const STORAGE_KEY = "has_seen_onboarding";

export function OnboardingProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);

  const openGuide = () => setIsOpen(true);
  const closeGuide = () => {
    setIsOpen(false);
    localStorage.setItem(STORAGE_KEY, "1");
  };
  const openIfFirstVisit = () => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setIsOpen(true);
    }
  };

  return (
    <OnboardingContext.Provider value={{ isOpen, openGuide, closeGuide, openIfFirstVisit }}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  return useContext(OnboardingContext);
}
