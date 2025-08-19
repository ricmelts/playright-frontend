import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Search, Plus, MessageCircle, Send, Archive, Star } from 'lucide-react';

export function MessagesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);

  const conversations = [
    {
      id: 1,
      name: 'Marcus Johnson',
      lastMessage: 'Thanks for the endorsement opportunity!',
      time: '2 hours ago',
      unread: true,
      avatar: 'https://images.unsplash.com/photo-1506629905607-c65eaa0a49b0?w=40&h=40&fit=crop&crop=face'
    },
    {
      id: 2,
      name: 'Nike Local Store',
      lastMessage: 'Contract details attached for review',
      time: '5 hours ago',
      unread: false,
      avatar: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=40&h=40&fit=crop'
    },
    {
      id: 3,
      name: 'Sarah Williams',
      lastMessage: 'When can we schedule the photoshoot?',
      time: '1 day ago',
      unread: true,
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face'
    }
  ];

  const messages = [
    {
      id: 1,
      sender: 'Marcus Johnson',
      content: 'Hi! I received your message about the Nike endorsement opportunity. This sounds really exciting!',
      time: '10:30 AM',
      isOwn: false
    },
    {
      id: 2,
      sender: 'You',
      content: 'Great! I think you\'d be a perfect fit for their local campaign. The terms are very competitive.',
      time: '10:35 AM',
      isOwn: true
    },
    {
      id: 3,
      sender: 'Marcus Johnson',
      content: 'Thanks for the endorsement opportunity! When do we start?',
      time: '2 hours ago',
      isOwn: false
    }
  ];

  const handleSendMessage = () => {
    // TODO: Implement send message functionality
    console.log('Send message functionality to be implemented');
  };

  const handleNewConversation = () => {
    // TODO: Implement new conversation functionality
    console.log('New conversation functionality to be implemented');
  };

  const handleArchiveMessage = () => {
    // TODO: Implement archive functionality
    console.log('Archive functionality to be implemented');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl tracking-tight mb-2">Messages</h1>
          <p className="text-muted-foreground">
            Communicate with athletes, brands, and partners.
          </p>
        </div>
        <Button onClick={handleNewConversation}>
          <Plus className="w-4 h-4 mr-2" />
          New Message
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* Conversations List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg">Conversations</CardTitle>
              <Badge variant="secondary">{conversations.length}</Badge>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="space-y-1">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => setSelectedMessage(conversation.id)}
                  className={`p-4 cursor-pointer hover:bg-muted/50 transition-colors border-b border-border/50 ${
                    selectedMessage === conversation.id ? 'bg-muted' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <img
                      src={conversation.avatar}
                      alt={conversation.name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium truncate">{conversation.name}</h3>
                        <span className="text-xs text-muted-foreground">{conversation.time}</span>
                      </div>
                      <p className="text-sm text-muted-foreground truncate mt-1">
                        {conversation.lastMessage}
                      </p>
                    </div>
                    {conversation.unread && (
                      <div className="w-2 h-2 bg-primary rounded-full"></div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Message Thread */}
        <Card className="lg:col-span-2">
          {selectedMessage ? (
            <>
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <img
                      src={conversations.find(c => c.id === selectedMessage)?.avatar}
                      alt="Avatar"
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div>
                      <h3 className="font-medium">
                        {conversations.find(c => c.id === selectedMessage)?.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">Online</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">
                      <Star className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleArchiveMessage}>
                      <Archive className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex flex-col h-[400px]">
                <div className="flex-1 overflow-y-auto space-y-4 py-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] p-3 rounded-lg ${
                          message.isOwn
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.isOwn ? 'text-primary-foreground/70' : 'text-muted-foreground'
                        }`}>
                          {message.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="border-t pt-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Type your message..."
                      className="flex-1"
                    />
                    <Button onClick={handleSendMessage}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </>
          ) : (
            <CardContent className="flex items-center justify-center h-full">
              <div className="text-center">
                <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Select a conversation</h3>
                <p className="text-muted-foreground">
                  Choose a conversation from the list to start messaging.
                </p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
}