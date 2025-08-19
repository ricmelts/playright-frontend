import { useState } from "react";
import { ThemeProvider } from "./components/ThemeProvider";
import { Layout } from "./components/Layout";
import { HomePage } from "./components/pages/HomePage";
import { PlayerSearchPage } from "./components/pages/PlayerSearchPage";
import { DealsPage } from "./components/pages/DealsPage";
import { MarketPage } from "./components/pages/MarketPage";
import { NewsPage } from "./components/pages/NewsPage";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <HomePage />;
      case "player-search":
        return <PlayerSearchPage />;
      case "deals":
        return <DealsPage />;
      case "market":
        return <MarketPage />;
      case "news":
        return <NewsPage />;
      case "messages":
        return (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <h2 className="text-2xl font-medium mb-2">
                Messages
              </h2>
              <p className="text-muted-foreground">
                Message center coming soon
              </p>
            </div>
          </div>
        );
      case "notifications":
        return (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <h2 className="text-2xl font-medium mb-2">
                Notifications
              </h2>
              <p className="text-muted-foreground">
                Notification center coming soon
              </p>
            </div>
          </div>
        );
      case "profile":
        return (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <h2 className="text-2xl font-medium mb-2">
                Profile
              </h2>
              <p className="text-muted-foreground">
                Profile management coming soon
              </p>
            </div>
          </div>
        );
      default:
        return <HomePage />;
    }
  };

  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=Stalinist+One&display=swap"
        rel="stylesheet"
      />
      <ThemeProvider
        defaultTheme="dark"
        storageKey="playright-ui-theme"
      >
        <div className="min-h-screen bg-background text-foreground">
          <Layout
            currentPage={currentPage}
            onPageChange={setCurrentPage}
          >
            {renderPage()}
          </Layout>
        </div>
      </ThemeProvider>
    </>
  );
}