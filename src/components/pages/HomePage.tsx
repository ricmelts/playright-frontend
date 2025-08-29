import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Users, DollarSign, Activity, ArrowRight } from 'lucide-react'
import { useQuery } from 'react-query'
import { apiClient } from '../../services/api'
import { useAuth } from '../../hooks/useAuth'

export function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuth()

  // Fetch platform analytics
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    'platformAnalytics',
    () => apiClient.getPlatformAnalytics(),
    {
      onError: (error) => {
        console.error('Error fetching analytics:', error);
      }
    }
  )

  // Fetch trending athletes
  const { data: trendingAthletes, isLoading: trendingLoading } = useQuery(
    'trendingAthletes',
    () => apiClient.getTrendingAthletes(undefined, 5),
    {
      onError: (error) => {
        console.error('Error fetching trending athletes:', error);
      }
    }
  )

  // Fetch recent deals
  const { data: recentDealsData, isLoading: dealsLoading } = useQuery(
    'recentDeals',
    () => apiClient.getDeals(1, 5, { status: 'active' }),
    {
      onError: (error) => {
        console.error('Error fetching deals:', error);
      }
    }
  )

  // Fallback stats if API is not available
  const defaultStats = [
    { label: 'Active Athletes', value: '1,247', icon: Users, change: '+12%' },
    { label: 'Total Deals', value: '$2.4M', icon: DollarSign, change: '+23%' },
    { label: 'Market Activity', value: '94%', icon: Activity, change: '+5%' },
    { label: 'Growth Rate', value: '18.2%', icon: TrendingUp, change: '+8%' }
  ]

  const stats = analyticsData ? [
    { 
      label: 'Active Athletes', 
      value: analyticsData.active_athletes?.toString() || '0', 
      icon: Users, 
      change: analyticsData.athlete_growth || '0%' 
    },
    { 
      label: 'Total Deal Value', 
      value: analyticsData.total_deal_value ? `$${(analyticsData.total_deal_value / 1000000).toFixed(1)}M` : '$0', 
      icon: DollarSign, 
      change: analyticsData.deal_value_growth || '0%' 
    },
    { 
      label: 'Active Campaigns', 
      value: analyticsData.active_campaigns?.toString() || '0', 
      icon: Activity, 
      change: analyticsData.campaign_growth || '0%' 
    },
    { 
      label: 'Success Rate', 
      value: analyticsData.success_rate ? `${analyticsData.success_rate.toFixed(1)}%` : '0%', 
      icon: TrendingUp, 
      change: analyticsData.success_rate_change || '0%' 
    }
  ] : defaultStats

  const recentDeals = recentDealsData?.items?.slice(0, 3) || [
    { athlete_name: 'Marcus Johnson', brand_name: 'Nike Local', value: 15000, sport: 'Basketball' },
    { athlete_name: 'Sarah Williams', brand_name: 'Adidas Regional', value: 12000, sport: 'Soccer' },
    { athlete_name: 'David Chen', brand_name: 'Local Fitness Co.', value: 8000, sport: 'Tennis' }
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

  if (analyticsLoading || trendingLoading || dealsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl tracking-tight mb-2">
          Welcome back, {user?.name || 'User'}!
        </h1>
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
                  <p className="font-medium">{deal.athlete_name || deal.player}</p>
                  <p className="text-sm text-muted-foreground">{deal.brand_name || deal.brand}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    {typeof deal.value === 'number' 
                      ? `$${deal.value.toLocaleString()}` 
                      : deal.value}
                  </p>
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