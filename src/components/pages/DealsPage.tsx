import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Progress } from '../ui/progress'
import { DollarSign, Clock, CheckCircle, AlertCircle, Plus, Calendar } from 'lucide-react'

export function DealsPage() {
  const activeDeals = [
    {
      id: 1,
      player: 'Marcus Johnson',
      brand: 'Nike Local Store',
      value: '$15,000',
      status: 'In Progress',
      progress: 75,
      deadline: '2025-09-15',
      sport: 'Basketball'
    },
    {
      id: 2,
      player: 'Sarah Williams', 
      brand: 'Adidas Regional',
      value: '$12,000',
      status: 'Pending Review',
      progress: 50,
      deadline: '2025-08-30',
      sport: 'Soccer'
    },
    {
      id: 3,
      player: 'David Chen',
      brand: 'Local Fitness Co.',
      value: '$8,000',
      status: 'Contract Signed',
      progress: 100,
      deadline: '2025-12-01',
      sport: 'Tennis'
    }
  ]

  const proposedDeals = [
    {
      id: 4,
      player: 'Emma Rodriguez',
      brand: 'Swim Gear Plus',
      value: '$6,000',
      status: 'Awaiting Response',
      sport: 'Swimming',
      proposed: '2025-08-15'
    },
    {
      id: 5,
      player: 'Alex Thompson',
      brand: 'Urban Athletic',
      value: '$10,000',
      status: 'Under Review',
      sport: 'Basketball',
      proposed: '2025-08-10'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Contract Signed':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'In Progress':
        return <Clock className="w-4 h-4 text-blue-600" />
      case 'Pending Review':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Contract Signed':
        return 'bg-green-100 text-green-800'
      case 'In Progress':
        return 'bg-blue-100 text-blue-800'
      case 'Pending Review':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl tracking-tight mb-2">Deals Management</h1>
          <p className="text-muted-foreground">
            Track and manage endorsement deals from proposal to completion.
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          New Deal
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Total Value</p>
                <p className="text-xl font-medium">$51K</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Active Deals</p>
                <p className="text-xl font-medium">3</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Pending</p>
                <p className="text-xl font-medium">2</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-sm text-muted-foreground">Due Soon</p>
                <p className="text-xl font-medium">1</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="active" className="space-y-4">
        <TabsList>
          <TabsTrigger value="active">Active Deals</TabsTrigger>
          <TabsTrigger value="proposed">Proposed</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {activeDeals.map((deal) => (
            <Card key={deal.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{deal.player} × {deal.brand}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary">{deal.sport}</Badge>
                      <span className="text-2xl font-medium text-green-600">{deal.value}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(deal.status)}
                    <Badge className={getStatusColor(deal.status)}>
                      {deal.status}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Progress</span>
                    <span>{deal.progress}%</span>
                  </div>
                  <Progress value={deal.progress} className="h-2" />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    Deadline: {deal.deadline}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">View Details</Button>
                    <Button size="sm">Update Status</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="proposed" className="space-y-4">
          {proposedDeals.map((deal) => (
            <Card key={deal.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{deal.player} × {deal.brand}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary">{deal.sport}</Badge>
                      <span className="text-2xl font-medium text-green-600">{deal.value}</span>
                    </div>
                  </div>
                  <Badge className={getStatusColor(deal.status)}>
                    {deal.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Proposed on {deal.proposed}
                  </p>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">Edit Proposal</Button>
                    <Button size="sm">Follow Up</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="completed">
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-center">
                <CheckCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No completed deals yet</h3>
                <p className="text-muted-foreground">Completed deals will appear here once finalized.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}