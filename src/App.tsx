import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './components/ThemeProvider';
import { Layout } from './components/Layout';
import { HomePage } from './components/pages/HomePage';
import { PlayerSearchPage } from './components/pages/PlayerSearchPage';
import { DealsPage } from './components/pages/DealsPage';
import { MarketPage } from './components/pages/MarketPage';
import { NewsPage } from './components/pages/NewsPage';
import { MessagesPage } from './components/pages/MessagesPage';
import { NotificationsPage } from './components/pages/NotificationsPage';
import { ProfilePage } from './components/pages/ProfilePage';

export default function App() {
  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=Stalinist+One&display=swap"
        rel="stylesheet"
      />
      <ThemeProvider defaultTheme="dark" storageKey="playright-ui-theme">
        <div className="min-h-screen bg-background text-foreground">
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/player-search" element={<PlayerSearchPage />} />
                <Route path="/deals" element={<DealsPage />} />
                <Route path="/market" element={<MarketPage />} />
                <Route path="/news" element={<NewsPage />} />
                <Route path="/account/messages" element={<MessagesPage />} />
                <Route path="/account/notifications" element={<NotificationsPage />} />
                <Route path="/account/profile" element={<ProfilePage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </Router>
        </div>
      </ThemeProvider>
    </>
  );
}