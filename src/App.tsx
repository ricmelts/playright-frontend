import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider } from './components/ThemeProvider';
import { AuthProvider } from './hooks/useAuth';
import { Layout } from './components/Layout';
import { HomePage } from './components/pages/HomePage';
import { PlayerSearchPage } from './components/pages/PlayerSearchPage';
import { DealsPage } from './components/pages/DealsPage';
import { MarketPage } from './components/pages/MarketPage';
import { NewsPage } from './components/pages/NewsPage';
import { MessagesPage } from './components/pages/MessagesPage';
import { NotificationsPage } from './components/pages/NotificationsPage';
import { ProfilePage } from './components/pages/ProfilePage';
import { SettingsPage } from './components/pages/SettingsPage';
import { LoginPage } from './components/pages/LoginPage';
import { RegisterPage } from './components/pages/RegisterPage';
import { ProtectedRoute } from './components/ProtectedRoute';

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider defaultTheme="system" storageKey="playright-ui-theme">
          <link
            href="https://fonts.googleapis.com/css2?family=Stalinist+One&display=swap"
            rel="stylesheet"
          />
          <div className="min-h-screen bg-background text-foreground">
            <Router>
              <Layout>
                <Routes>
                  {/* Public routes */}
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  
                  {/* Protected routes */}
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <HomePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/player-search"
                    element={
                      <ProtectedRoute>
                        <PlayerSearchPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/deals"
                    element={
                      <ProtectedRoute>
                        <DealsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/market"
                    element={
                      <ProtectedRoute>
                        <MarketPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/news"
                    element={
                      <ProtectedRoute>
                        <NewsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/account/messages"
                    element={
                      <ProtectedRoute>
                        <MessagesPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/account/notifications"
                    element={
                      <ProtectedRoute>
                        <NotificationsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/account/profile"
                    element={
                      <ProtectedRoute>
                        <ProfilePage />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/account/settings"
                    element={
                      <ProtectedRoute>
                        <SettingsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </Router>
          </div>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}