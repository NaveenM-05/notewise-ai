import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Initialize user state based on token presence
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('jwt_token');
    return token ? { name: 'User' } : null;
  });

  const login = (userData) => {
    // The backend returns { access_token: "...", token_type: "bearer" }
    if (userData && userData.access_token) {
      console.log("Saving token to localStorage:", userData.access_token); // Debug log
      localStorage.setItem('jwt_token', userData.access_token);
      setUser({ name: 'User' });
    } else {
      console.error("Login failed: No access_token received", userData);
    }
  };

  const logout = () => {
    console.log("Logging out...");
    localStorage.removeItem('jwt_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};