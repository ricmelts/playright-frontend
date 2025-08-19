import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { TrendingUp, TrendingDown, Activity, Target, BarChart3, PieChart } from 'lucide-react'

export function MarketPage() {
  const marketTrends = [
    {
      sport: 'Basketball',
      trend: 'up',
      change: '+15%',
      value: '$2.4M',
      deals: 156,
      avgDeal: '$15.4K'
    },
    {
      sport: 'Soccer',
      trend: 'up',
      change: '+8%',
      value: '$1.8M',
      deals: 203,
      avgDeal: '$8.9K'
    },
    {
      sport: 'Tennis',
      trend: 'down',
      change: '-3%',
      value: '$980K',
      deals: 67,
      avgDeal: '$14.6K'
    },
    {
      sport: 'Swimming',
      trend: 'up',
      change: '+22%',
      value: '$650K',
      deals: 89,
      avgDeal: '$7.3K'
    }
  ]

  const topBrands = [
    { name: 'Nike Local Stores', deals: 45, value: '$680K', growth: '+18%' },
    { name: 'Adidas Regional', deals: 38, value: '$520K', growth: '+12%' },
    { name: 'Under Armour Local', deals: 29, value: '$435K', growth: '+25%' },
    { name: 'Local Fitness Chains', deals: 67, value: '$380K', growth: '+8%' }
  ]

  const opportunityAreas = [
    { area: 'Women\'s Basketball', potential: 'High', growth: '+35%', description: 'Rapidly growing market with high engagement' },
    { area: 'Youth Soccer', potential: 'Medium', growth: '+20%', description: 'Strong local community presence' },
    { area: 'E-Sports Athletes', potential: 'High', growth: '+65%', description: 'Emerging market with tech-savvy audience' },
    { area: 'Fitness Influencers', potential: 'Medium', growth: '+15%', description: 'Consistent engagement across demographics' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl tracking-tight mb-2">Market Intelligence</h1>
        <p className="text-muted-foreground">
          AI-powered insights into sports endorsement market trends and opportunities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Market Activity</p>
                <p className="text-xl font-medium">94.2%</p>
                <p className="text-xs text-green-600">+5.1% vs last month</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Match Rate</p>
                <p className="text-xl font-medium">78%</p>
                <p className="text-xs text-green-600">+3.2% vs last month</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm text-muted-foreground">Avg Deal Size</p>
                <p className="text-xl font-medium">$11.2K</p>
                <p className="text-xs text-green-600">+12% vs last month</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-xl font-medium">85%</p>
                <p className="text-xs text-green-600">+2.8% vs last month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Sport Market Trends
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {marketTrends.map((trend, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-muted/20">
                <div className="flex items-center gap-3">
                  <Badge variant="secondary">{trend.sport}</Badge>
                  <div>
                    <p className="font-medium">{trend.value}</p>
                    <p className="text-sm text-muted-foreground">{trend.deals} deals</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1">
                    {trend.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-600" />
                    )}
                    <span className={`text-sm font-medium ${trend.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                      {trend.change}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">Avg: {trend.avgDeal}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Performing Brands</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {topBrands.map((brand, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-muted/20">
                <div>
                  <p className="font-medium">{brand.name}</p>
                  <p className="text-sm text-muted-foreground">{brand.deals} deals • {brand.value}</p>
                </div>
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">{brand.growth}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Market Opportunities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {opportunityAreas.map((opportunity, index) => (
              <div key={index} className="p-4 rounded-lg border border-border/50 bg-muted/20">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium">{opportunity.area}</h3>
                  <div className="flex items-center gap-2">
                    <Badge variant={opportunity.potential === 'High' ? 'default' : 'secondary'}>
                      {opportunity.potential} Potential
                    </Badge>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3 text-green-600" />
                      <span className="text-sm text-green-600">{opportunity.growth}</span>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{opportunity.description}</p>
                <Button size="sm" variant="outline" className="w-full">
                  Explore Opportunity
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}