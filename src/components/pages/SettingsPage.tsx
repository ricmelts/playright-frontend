import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { ThemeToggle } from '../ThemeToggle';
import { 
  Bell, 
  Shield, 
  Database, 
  Palette, 
  Mail,
  Smartphone,
  Monitor,
  Save,
  RefreshCw,
  Download
} from 'lucide-react';

export function SettingsPage() {
  const [settings, setSettings] = useState({
    // Appearance
    theme: 'system',
    fontSize: 'medium',
    compactMode: false,
    
    // Notifications
    emailNotifications: true,
    pushNotifications: true,
    marketingEmails: false,
    weeklyReports: true,
    dealAlerts: true,
    playerUpdates: true,
    
    // Privacy & Security
    twoFactorAuth: false,
    sessionTimeout: '30',
    dataSharing: false,
    analyticsTracking: true,
    
    // Data & Storage
    autoBackup: true,
    dataRetention: '12',
    exportFormat: 'csv'
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    // TODO: Save to database
    console.log(`Setting ${key} changed to:`, value);
  };

  const handleSaveSettings = () => {
    // TODO: Implement save settings to database
    console.log('Saving settings:', settings);
  };

  const handleResetSettings = () => {
    // TODO: Implement reset to defaults
    console.log('Resetting settings to defaults');
  };

  const handleExportData = () => {
    // TODO: Implement CSV data export from database
    // This should export user data, deals, players, etc. in CSV format
    console.log('Exporting user data as CSV');
    
    // Placeholder CSV export logic
    const csvData = [
      ['Type', 'Name', 'Value', 'Date'],
      ['Deal', 'Marcus Johnson x Nike', '$15,000', '2025-01-15'],
      ['Deal', 'Sarah Williams x Adidas', '$12,000', '2025-01-10'],
      ['Player', 'David Chen', 'Tennis', '2025-01-05'],
      // TODO: Replace with actual database data
    ];
    
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `playright-data-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl tracking-tight mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account preferences and application settings.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleResetSettings}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSaveSettings}>
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs defaultValue="appearance" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="appearance">
            <Palette className="w-4 h-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="data">
            <Database className="w-4 h-4 mr-2" />
            Data
          </TabsTrigger>
        </TabsList>

        <TabsContent value="appearance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Theme & Display</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Theme</Label>
                  <p className="text-sm text-muted-foreground">Choose your preferred theme</p>
                </div>
                <ThemeToggle />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Font Size</Label>
                  <p className="text-sm text-muted-foreground">Adjust text size for better readability</p>
                </div>
                <Select 
                  value={settings.fontSize} 
                  onValueChange={(value) => handleSettingChange('fontSize', value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="small">Small</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="large">Large</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">Reduce spacing for more content</p>
                </div>
                <Switch
                  checked={settings.compactMode}
                  onCheckedChange={(checked) => handleSettingChange('compactMode', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <Label className="text-base">Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                  </div>
                </div>
                <Switch
                  checked={settings.emailNotifications}
                  onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Smartphone className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <Label className="text-base">Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive push notifications</p>
                  </div>
                </div>
                <Switch
                  checked={settings.pushNotifications}
                  onCheckedChange={(checked) => handleSettingChange('pushNotifications', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <Label className="text-base">Deal Alerts</Label>
                    <p className="text-sm text-muted-foreground">Get notified about new deals</p>
                  </div>
                </div>
                <Switch
                  checked={settings.dealAlerts}
                  onCheckedChange={(checked) => handleSettingChange('dealAlerts', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Monitor className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <Label className="text-base">Player Updates</Label>
                    <p className="text-sm text-muted-foreground">Notifications about player changes</p>
                  </div>
                </div>
                <Switch
                  checked={settings.playerUpdates}
                  onCheckedChange={(checked) => handleSettingChange('playerUpdates', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Marketing Emails</Label>
                  <p className="text-sm text-muted-foreground">Receive promotional content</p>
                </div>
                <Switch
                  checked={settings.marketingEmails}
                  onCheckedChange={(checked) => handleSettingChange('marketingEmails', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Weekly Reports</Label>
                  <p className="text-sm text-muted-foreground">Get weekly performance summaries</p>
                </div>
                <Switch
                  checked={settings.weeklyReports}
                  onCheckedChange={(checked) => handleSettingChange('weeklyReports', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security & Privacy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Two-Factor Authentication</Label>
                  <p className="text-sm text-muted-foreground">Add extra security to your account</p>
                </div>
                <Switch
                  checked={settings.twoFactorAuth}
                  onCheckedChange={(checked) => handleSettingChange('twoFactorAuth', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Session Timeout</Label>
                  <p className="text-sm text-muted-foreground">Auto-logout after inactivity (minutes)</p>
                </div>
                <Select 
                  value={settings.sessionTimeout} 
                  onValueChange={(value) => handleSettingChange('sessionTimeout', value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15">15 min</SelectItem>
                    <SelectItem value="30">30 min</SelectItem>
                    <SelectItem value="60">1 hour</SelectItem>
                    <SelectItem value="120">2 hours</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Data Sharing</Label>
                  <p className="text-sm text-muted-foreground">Share anonymized data for improvements</p>
                </div>
                <Switch
                  checked={settings.dataSharing}
                  onCheckedChange={(checked) => handleSettingChange('dataSharing', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Analytics Tracking</Label>
                  <p className="text-sm text-muted-foreground">Help us improve with usage analytics</p>
                </div>
                <Switch
                  checked={settings.analyticsTracking}
                  onCheckedChange={(checked) => handleSettingChange('analyticsTracking', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Auto Backup</Label>
                  <p className="text-sm text-muted-foreground">Automatically backup your data</p>
                </div>
                <Switch
                  checked={settings.autoBackup}
                  onCheckedChange={(checked) => handleSettingChange('autoBackup', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Data Retention</Label>
                  <p className="text-sm text-muted-foreground">How long to keep your data (months)</p>
                </div>
                <Select 
                  value={settings.dataRetention} 
                  onValueChange={(value) => handleSettingChange('dataRetention', value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="6">6 months</SelectItem>
                    <SelectItem value="12">1 year</SelectItem>
                    <SelectItem value="24">2 years</SelectItem>
                    <SelectItem value="0">Forever</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Data Export</Label>
                  <p className="text-sm text-muted-foreground">Export your data in CSV format</p>
                </div>
                <Button onClick={handleExportData} variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
              </div>

              <div className="pt-4 border-t">
                <Button onClick={handleExportData} className="w-full">
                  <Database className="w-4 h-4 mr-2" />
                  Download All Data (CSV)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}