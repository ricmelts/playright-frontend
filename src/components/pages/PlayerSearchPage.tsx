import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Search, MapPin, Star, TrendingUp, Eye } from 'lucide-react'

export function PlayerSearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [sportFilter, setSportFilter] = useState('')
  const [locationFilter, setLocationFilter] = useState('')

  const players = [
    {
      id: 1,
      name: 'Marcus Johnson',
      sport: 'Basketball',
      location: 'Los Angeles, CA',
      rating: 4.8,
      followers: '125K',
      engagement: '8.4%',
      price: '$5K-15K',
      image: 'https://images.unsplash.com/photo-1506629905607-c65eaa0a49b0?w=300&h=300&fit=crop&crop=face'
    },
    {
      id: 2,
      name: 'Sarah Williams',
      sport: 'Soccer',
      location: 'Austin, TX',
      rating: 4.6,
      followers: '89K',
      engagement: '7.2%',
      price: '$3K-12K',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face'
    },
    {
      id: 3,
      name: 'David Chen',
      sport: 'Tennis',
      location: 'Miami, FL',
      rating: 4.9,
      followers: '156K',
      engagement: '9.1%',
      price: '$8K-20K',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face'
    },
    {
      id: 4,
      name: 'Emma Rodriguez',
      sport: 'Swimming',
      location: 'San Diego, CA',
      rating: 4.7,
      followers: '67K',
      engagement: '6.8%',
      price: '$2K-8K',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop&crop=face'
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl tracking-tight mb-2">Player Search</h1>
        <p className="text-muted-foreground">
          Discover talented athletes for your endorsement campaigns using AI-powered matching.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search players by name, sport, or skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <Select value={sportFilter} onValueChange={setSportFilter}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Sport" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="basketball">Basketball</SelectItem>
                <SelectItem value="soccer">Soccer</SelectItem>
                <SelectItem value="tennis">Tennis</SelectItem>
                <SelectItem value="swimming">Swimming</SelectItem>
                <SelectItem value="football">Football</SelectItem>
              </SelectContent>
            </Select>
            <Select value={locationFilter} onValueChange={setLocationFilter}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Location" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="california">California</SelectItem>
                <SelectItem value="texas">Texas</SelectItem>
                <SelectItem value="florida">Florida</SelectItem>
                <SelectItem value="newyork">New York</SelectItem>
              </SelectContent>
            </Select>
            <Button className="w-full md:w-auto">
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {players.map((player) => (
          <Card key={player.id} className="group hover:shadow-lg transition-all duration-200">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full overflow-hidden bg-muted">
                  <img 
                    src={player.image} 
                    alt={player.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{player.name}</h3>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <MapPin className="w-3 h-3" />
                    {player.location}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-yellow-500 fill-current" />
                  <span className="text-xs">{player.rating}</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <Badge variant="secondary">{player.sport}</Badge>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-muted-foreground">Followers</p>
                  <p className="font-medium">{player.followers}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Engagement</p>
                  <p className="font-medium text-green-600">{player.engagement}</p>
                </div>
              </div>
              
              <div className="border-t pt-3">
                <p className="text-sm text-muted-foreground mb-2">Endorsement Range</p>
                <p className="font-medium">{player.price}</p>
              </div>
              
              <div className="flex gap-2">
                <Button size="sm" className="flex-1">
                  <Eye className="w-4 h-4 mr-1" />
                  View Profile
                </Button>
                <Button size="sm" variant="outline">
                  <TrendingUp className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}