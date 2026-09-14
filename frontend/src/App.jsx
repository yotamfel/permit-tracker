import { useEffect, lazy, Suspense } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { trackPageView } from "./lib/analytics";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Browse from "./pages/Browse";
import DestinationDetail from "./pages/DestinationDetail";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Account from "./pages/Account";
import Contact from "./pages/Contact";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import NotFound from "./pages/NotFound";
import OnboardingGuide from "./components/OnboardingGuide";
import CookieConsent from "./components/CookieConsent";

// Lazy-loaded: Admin pulls in recharts (a sizeable charting library only
// ever used on this one admin-only page) - splitting it out keeps it out of
// the bundle every regular visitor and guest downloads.
const Admin = lazy(() => import("./pages/Admin"));
const AdminDestinationEdit = lazy(() => import("./pages/AdminDestinationEdit"));

export default function App() {
  const location = useLocation();

  useEffect(() => {
    trackPageView(location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-stone-50 dark:bg-stone-950">
      <Header />
      <OnboardingGuide />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalog" element={<Browse />} />
          <Route path="/destinations/:id" element={<DestinationDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/account" element={<Account />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route
            path="/admin"
            element={
              <Suspense fallback={null}>
                <Admin />
              </Suspense>
            }
          />
          <Route
            path="/admin/destinations/:id"
            element={
              <Suspense fallback={null}>
                <AdminDestinationEdit />
              </Suspense>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
      <CookieConsent />
    </div>
  );
}
