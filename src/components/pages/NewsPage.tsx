import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Clock, ExternalLink, TrendingUp, Bookmark } from 'lucide-react'

export function NewsPage() {
  const industryNews = [
    {
      id: 1,
      title: 'Local Sports Marketing Sees 35% Growth in Q3',
      summary: 'Regional endorsement deals are outpacing national campaigns as brands focus on community engagement and authentic local connections.',
      source: 'Sports Business Journal',
      time: '2 hours ago',
      category: 'Market Trends',
      image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&h=200&fit=crop'
    },
    {
      id: 2,
      title: 'AI Revolutionizes Athlete-Brand Matching',
      summary: 'New machine learning algorithms are helping agencies achieve 85% success rates in endorsement deal negotiations.',
      source: 'TechSport Today',
      time: '4 hours ago',
      category: 'Technology',
      image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=200&fit=crop'
    },
    {
      id: 3,
      title: 'Women\'s Sports Endorsements Break Records',
      summary: 'Female athletes are commanding higher endorsement values than ever before, with deals up 40% year-over-year.',
      source: 'Athletic Business',
      time: '6 hours ago',
      category: 'Industry News',
      image: 'https://images.unsplash.com/photo-1594736797933-d0d15a0e2dee?w=400&h=200&fit=crop'
    },
    {
      id: 4,
      title: 'Micro-Influencer Athletes Drive Local Engagement',
      summary: 'Athletes with smaller but highly engaged followings are delivering better ROI for local businesses.',
      source: 'Marketing Today',
      time: '8 hours ago',
      category: 'Strategy',
      image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop'
    }
  ]

  const trendingTopics = [
    { topic: 'NIL Deals', mentions: 2847, change: '+23%' },
    { topic: 'Local Endorsements', mentions: 1956, change: '+45%' },
    { topic: 'Social Media ROI', mentions: 1734, change: '+12%' },
    { topic: 'Athlete Analytics', mentions: 1523, change: '+67%' },
    { topic: 'Brand Partnerships', mentions: 1401, change: '+8%' }
  ]

  const marketUpdates = [
    {
      title: 'Basketball Market Alert',
      content: 'Local basketball endorsements up 28% this quarter. Recommended focus on collegiate players.',
      type: 'opportunity',
      time: '1 hour ago'
    },
    {
      title: 'Soccer Season Prep',
      content: 'MLS season approaching. Brands increasing investment in local soccer talent.',
      type: 'insight',
      time: '3 hours ago'
    },
    {
      title: 'Swimming Championship Impact',
      content: 'Regional swimming championships driving 15% increase in aquatic sport endorsements.',
      type: 'trend',
      time: '5 hours ago'
    }
  ]

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Market Trends':
        return 'bg-blue-100 text-blue-800'
      case 'Technology':
        return 'bg-purple-100 text-purple-800'
      case 'Industry News':
        return 'bg-green-100 text-green-800'
      case 'Strategy':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl tracking-tight mb-2">Industry News</h1>
        <p className="text-muted-foreground">
          Stay updated with the latest trends and insights in sports marketing and endorsements.
        </p>
      </div>

      <Tabs defaultValue="news" className="space-y-4">
        <TabsList>
          <TabsTrigger value="news">Latest News</TabsTrigger>
          <TabsTrigger value="trends">Trending</TabsTrigger>
          <TabsTrigger value="market">Market Updates</TabsTrigger>
        </TabsList>

        <TabsContent value="news" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              {industryNews.map((article) => (
                <Card key={article.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-0">
                    <div className="flex flex-col md:flex-row">
                      <div className="md:w-48 h-48 md:h-auto">
                        <img 
                          src={article.image} 
                          alt={article.title}
                          className="w-full h-full object-cover rounded-t-lg md:rounded-l-lg md:rounded-t-none"
                        />
                      </div>
                      <div className="flex-1 p-6">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getCategoryColor(article.category)}>
                            {article.category}
                          </Badge>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {article.time}
                          </div>
                        </div>
                        <h3 className="text-lg font-medium mb-2">{article.title}</h3>
                        <p className="text-muted-foreground mb-4 line-clamp-2">{article.summary}</p>
                        <div className="flex items-center justify-between">
                          <p className="text-sm text-muted-foreground">Source: {article.source}</p>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="sm">
                              <Bookmark className="w-4 h-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <ExternalLink className="w-4 h-4 mr-1" />
                              Read More
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Updates</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {marketUpdates.map((update, index) => (
                    <div key={index} className="p-3 rounded-lg border border-border/50 bg-muted/20">
                      <h4 className="font-medium text-sm mb-1">{update.title}</h4>
                      <p className="text-xs text-muted-foreground mb-2">{update.content}</p>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-xs">
                          {update.type}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{update.time}</span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Trending Topics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {trendingTopics.map((topic, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-muted/20">
                    <div>
                      <h3 className="font-medium">{topic.topic}</h3>
                      <p className="text-sm text-muted-foreground">{topic.mentions.toLocaleString()} mentions</p>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-600">{topic.change}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="market" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {marketUpdates.map((update, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{update.title}</CardTitle>
                    <Badge variant="outline">{update.type}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">{update.content}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{update.time}</span>
                    <Button size="sm" variant="outline">
                      Learn More
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}