import React from "react";
import { Navigate, useLocation } from "react-router-dom";

const getAuthStatus = () => {
  const token = localStorage.getItem("token");
  const storedUser = localStorage.getItem("user");
  
  if (!token || !storedUser) {
    return { isAuthenticated: false, isAdmin: false };
  }

  try {
    const user = JSON.parse(storedUser);
    return {
      isAuthenticated: true,
      isAdmin: !!user.is_admin,
    };
  } catch (error) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return { isAuthenticated: false, isAdmin: false };
  }
};

export default function AdminRoute({ children }) {
  const location = useLocation();
  const { isAuthenticated, isAdmin } = getAuthStatus();

  if (!isAuthenticated || !isAdmin) {
    return <Navigate to="/admin-login" state={{ from: location }} replace />;
  }

  return children;
}