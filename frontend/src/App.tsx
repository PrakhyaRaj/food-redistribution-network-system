import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import AddFood from "./pages/AddFood";
import MyFoods from "./pages/MyFoods";
import AddRequest from "./pages/AddRequest";
import MyRequests from "./pages/MyRequests";
import Transactions from "./pages/Transactions";
import NotFound from "./pages/NotFound";
import Profile from "./pages/Profile";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/profile" element={<Profile/>} />
            <Route
              path="/food/add"
              element={
                <ProtectedRoute>
                  <AddFood />
                </ProtectedRoute>
              }
            />
            <Route
              path="/food/my"
              element={
                <ProtectedRoute>
                  <MyFoods />
                </ProtectedRoute>
              }
            />
            <Route
              path="/requests/add"
              element={
                <ProtectedRoute>
                  <AddRequest />
                </ProtectedRoute>
              }
            />
            <Route
              path="/requests/my"
              element={
                <ProtectedRoute>
                  <MyRequests />
                </ProtectedRoute>
              }
            />
            <Route
              path="/transactions"
              element={
                <ProtectedRoute>
                  <Transactions />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
