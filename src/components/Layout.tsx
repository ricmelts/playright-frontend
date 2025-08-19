import { useState } from 'react'
import { Home, Search, DollarSign, TrendingUp, MessageSquare, Bell, User, Menu } from 'lucide-react'
import { Button } from './ui/button'
import { ThemeToggle } from './ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
  currentPage: string
  onPageChange: (page: string) => void
}

export function Layout({ children, currentPage, onPageChange }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const mainPages = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'player-search', label: 'Player Search', icon: Search },
    { id: 'deals', label: 'Deals', icon: DollarSign },
    { id: 'market', label: 'Market', icon: TrendingUp },
    { id: 'news', label: 'News', icon: MessageSquare }
  ]

  const utilityPages = [
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'profile', label: 'Profile', icon: User }
  ]

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
                variant={currentPage === page.id ? "secondary" : "ghost"}
                onClick={() => onPageChange(page.id)}
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
                variant={currentPage === page.id ? "secondary" : "ghost"}
                onClick={() => onPageChange(page.id)}
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
              <Button variant="ghost" size="sm" className="text-muted-foreground">
                <Bell className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="text-muted-foreground">
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
  )
}