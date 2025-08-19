import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Search, DollarSign, TrendingUp, MessageSquare, Bell, User, Menu, Newspaper, Settings } from 'lucide-react';
import { Button } from './ui/button';
import { ThemeToggle } from './ThemeToggle';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const mainPages = [
    { id: 'home', label: 'Home', icon: Home, path: '/' },
    { id: 'player-search', label: 'Player Search', icon: Search, path: '/player-search' },
    { id: 'deals', label: 'Deals', icon: DollarSign, path: '/deals' },
    { id: 'market', label: 'Market', icon: TrendingUp, path: '/market' },
    { id: 'news', label: 'News', icon: Newspaper, path: '/news' }
  ];

  const utilityPages = [
    { id: 'messages', label: 'Messages', icon: MessageSquare, path: '/account/messages' },
    { id: 'notifications', label: 'Notifications', icon: Bell, path: '/account/notifications' },
    { id: 'profile', label: 'Profile', icon: User, path: '/account/profile' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/account/settings' }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const isCurrentPage = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 ease-in-out bg-sidebar border-r border-border/50 flex flex-col`}>
        {/* Header */}
        <div className="border-b border-border/50 p-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary via-muted-foreground to-primary rounded-sm flex items-center justify-center">
              <div className="w-4 h-4 bg-background rounded-sm"></div>
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-['Stalinist_One'] text-lg tracking-tight">PlayRight</h1>
                <p className="text-xs text-muted-foreground">.ai</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Navigation */}
        <div className="flex-1 px-3 py-4">
          <div className="mb-6">
            {sidebarOpen && <p className="text-xs text-muted-foreground mb-2 px-3">Main</p>}
            {mainPages.map((page) => (
              <Button
                key={page.id}
                variant={isCurrentPage(page.path) ? "secondary" : "ghost"}
                onClick={() => handleNavigation(page.path)}
                className="w-full justify-start mb-1"
              >
                <page.icon className="w-4 h-4" />
                {sidebarOpen && <span className="ml-3">{page.label}</span>}
              </Button>
            ))}
          </div>
          
          <div>
            {sidebarOpen && <p className="text-xs text-muted-foreground mb-2 px-3">Account</p>}
            {utilityPages.map((page) => (
              <Button
                key={page.id}
                variant={isCurrentPage(page.path) ? "secondary" : "ghost"}
                onClick={() => handleNavigation(page.path)}
                className="w-full justify-start mb-1"
              >
                <page.icon className="w-4 h-4" />
                {sidebarOpen && <span className="ml-3">{page.label}</span>}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        <header className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex h-16 items-center px-6">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="mr-4"
            >
              <Menu className="w-4 h-4" />
            </Button>
            <div className="ml-auto flex items-center gap-4">
              <ThemeToggle />
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-muted-foreground"
                onClick={() => handleNavigation('/account/notifications')}
              >
                <Bell className="w-4 h-4" />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-muted-foreground"
                onClick={() => handleNavigation('/account/profile')}
              >
                <User className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </header>
        
        <div className="flex-1 p-6">
          {children}
        </div>
      </main>
    </div>
  );
}