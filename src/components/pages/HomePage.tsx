import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Users, DollarSign, Activity, ArrowRight } from 'lucide-react'

export function HomePage() {
  const navigate = useNavigate()

  const stats = [
    { label: 'Active Players', value: '1,247', icon: Users, change: '+12%' },
    { label: 'Total Deals', value: '$2.4M', icon: DollarSign, change: '+23%' },
    { label: 'Market Activity', value: '94%', icon: Activity, change: '+5%' },
    { label: 'Growth Rate', value: '18.2%', icon: TrendingUp, change: '+8%' }
  ]

  const recentDeals = [
    { player: 'Marcus Johnson', brand: 'Nike Local', value: '$15K', sport: 'Basketball' },
    { player: 'Sarah Williams', brand: 'Adidas Regional', value: '$12K', sport: 'Soccer' },
    { player: 'David Chen', brand: 'Local Fitness Co.', value: '$8K', sport: 'Tennis' }
  ]

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'players':
        navigate('/player-search')
        break
      case 'deals':
        navigate('/deals')
        break
      case 'market':
        navigate('/market')
        break
      case 'report':
        // TODO: Implement report generation
        console.log('Generate report functionality to be implemented')
        break
      default:
        break
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl tracking-tight mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          AI-powered sports agency connecting athletes with local endorsement opportunities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm">{stat.label}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl mb-1">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">{stat.change}</span> from last month
              </p>
            </CardContent>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary/20 to-primary/5"></div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Deals</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentDeals.map((deal, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-muted/20">
                <div>
                  <p className="font-medium">{deal.player}</p>
                  <p className="text-sm text-muted-foreground">{deal.brand}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{deal.value}</p>
                  <Badge variant="secondary" className="text-xs">{deal.sport}</Badge>
                </div>
              </div>
            ))}
            <Button 
              variant="ghost" 
              className="w-full justify-between"
              onClick={() => navigate('/deals')}
            >
              View All Deals
              <ArrowRight className="w-4 h-4" />
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => handleQuickAction('players')}
            >
              <Users className="w-4 h-4 mr-2" />
              Find New Players
            </Button>
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => handleQuickAction('deals')}
            >
              <DollarSign className="w-4 h-4 mr-2" />
              Create Deal Proposal
            </Button>
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => handleQuickAction('market')}
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Market Analysis
            </Button>
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => handleQuickAction('report')}
            >
              <Activity className="w-4 h-4 mr-2" />
              Generate Report
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}