import { Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Browse from "./pages/Browse";
import DestinationDetail from "./pages/DestinationDetail";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Account from "./pages/Account";
import Admin from "./pages/Admin";
import Contact from "./pages/Contact";

export default function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <Routes>
        <Route path="/" element={<Browse />} />
        <Route path="/destinations/:id" element={<DestinationDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/account" element={<Account />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </div>
  );
}
