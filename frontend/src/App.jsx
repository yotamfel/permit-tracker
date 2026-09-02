import { useEffect } from "react";
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
import Admin from "./pages/Admin";
import AdminDestinationEdit from "./pages/AdminDestinationEdit";
import Contact from "./pages/Contact";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import NotFound from "./pages/NotFound";
import OnboardingGuide from "./components/OnboardingGuide";
import CookieConsent from "./components/CookieConsent";

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
          <Route path="/admin" element={<Admin />} />
          <Route path="/admin/destinations/:id" element={<AdminDestinationEdit />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
      <CookieConsent />
    </div>
  );
}
