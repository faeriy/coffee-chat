import React, { useCallback, useEffect, useState } from "react";
import LoginPage from "./LoginPage";
import ChatExamplesPage from "./ChatExamplesPage";
import { AUTH_TOKEN_KEY, setAuthToken } from "./apiClient";

/**
 * Shows login page when not authenticated, and chat examples page after
 * successful login (JWT or Google). Token is read from localStorage on load
 * and from URL on return from Google OAuth (so refresh keeps you logged in).
 */
const App: React.FC = () => {
  const [isAuthenticated, setAuthenticated] = useState<boolean>(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) return true;
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");
    if (urlToken) {
      localStorage.setItem(AUTH_TOKEN_KEY, urlToken);
      return true;
    }
    return false;
  });

  const restoreToken = useCallback(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      setAuthToken(token);
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");
    if (urlToken) {
      localStorage.setItem(AUTH_TOKEN_KEY, urlToken);
      setAuthToken(urlToken);
      setAuthenticated(true);
      window.history.replaceState({}, document.title, window.location.pathname || "/");
    }
  }, []);

  useEffect(() => {
    restoreToken();
  }, [restoreToken]);

  const handleLoginSuccess = useCallback(() => {
    setAuthenticated(true);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setAuthToken(null);
    setAuthenticated(false);
  }, []);

  if (isAuthenticated) {
    return <ChatExamplesPage onLogout={handleLogout} />;
  }
  return <LoginPage onLoginSuccess={handleLoginSuccess} />;
};

export default App;
