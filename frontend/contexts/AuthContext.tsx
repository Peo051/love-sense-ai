'use client';

import { getIdToken, onAuthStateChanged, type User } from 'firebase/auth';
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { auth } from '@/lib/firebase';
import { clearAuthToken, hasAuthToken, saveAuthToken, setAuthTokenProvider } from '@/lib/api';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function createFallbackAuthContext(): AuthContextValue {
  return {
    user: null,
    loading: false,
    isAuthenticated: hasAuthToken(),
    getToken: async () => {
      if (typeof window === 'undefined') {
        return null;
      }
      return window.localStorage.getItem('love_emotion_auth_token');
    },
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const getToken = useCallback(async () => {
    const currentUser = auth.currentUser;
    if (!currentUser) {
      return null;
    }

    const token = await getIdToken(currentUser, true);
    saveAuthToken(token);
    return token;
  }, []);

  useEffect(() => {
    setAuthTokenProvider(getToken);
    return () => setAuthTokenProvider(null);
  }, [getToken]);

  useEffect(() => {
    let isMounted = true;
    const unsubscribe = onAuthStateChanged(auth, async (nextUser) => {
      if (!isMounted) {
        return;
      }

      setUser(nextUser);

      try {
        if (nextUser) {
          const token = await getIdToken(nextUser, true);
          saveAuthToken(token);
        } else {
          clearAuthToken();
        }
      } catch {
        clearAuthToken();
      }

      if (isMounted) {
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
      unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user) || hasAuthToken(),
      getToken,
    }),
    [getToken, loading, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext) ?? createFallbackAuthContext();
}
