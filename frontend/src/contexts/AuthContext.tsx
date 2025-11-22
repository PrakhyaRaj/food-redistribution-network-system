import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface AuthContextType {
  userId: string | null;
  roles: string[];
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone: string;
  location_lat: number;
  location_long: number;
  roles: string[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [userId, setUserId] = useState<string | null>(
    localStorage.getItem("user_id")
  );
  const [roles, setRoles] = useState<string[]>(
    JSON.parse(localStorage.getItem("roles") || "[]")
  );
  const navigate = useNavigate();

  const isAuthenticated = !!userId;

  const login = async (email: string, password: string) => {
    try {
      const response = await api.auth.login(email, password);
      localStorage.setItem("user_id", response.user_id.toString());
      localStorage.setItem("roles", JSON.stringify(response.roles));
      setUserId(response.user_id.toString());
      setRoles(response.roles);
      toast.success("Login successful!");
      navigate("/dashboard");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed");
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      await api.auth.register(data);
      toast.success("Registration successful! Please login.");
      navigate("/login");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Registration failed");
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("roles");
    setUserId(null);
    setRoles([]);
    toast.success("Logged out successfully");
    navigate("/login");
  };

  return (
    <AuthContext.Provider
      value={{ userId, roles, isAuthenticated, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
