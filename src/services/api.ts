/**
 * API Client Service for PlayRight Frontend
 * Handles communication with backend API, AI engine, and PocketBase
 */

interface APIConfig {
  apiUrl: string;
  aiApiUrl: string;
  pocketbaseUrl: string;
}

class APIClient {
  private config: APIConfig;
  private authToken: string | null = null;

  constructor() {
    this.config = {
      apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      aiApiUrl: process.env.REACT_APP_AI_API_URL || 'http://localhost:8001',
      pocketbaseUrl: process.env.REACT_APP_POCKETBASE_URL || 'http://localhost:8090',
    };
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  clearAuthToken() {
    this.authToken = null;
  }

  private async request(url: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication APIs
  async login(email: string, password: string) {
    return this.request(`${this.config.apiUrl}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    role: 'athlete' | 'brand';
    name: string;
  }) {
    return this.request(`${this.config.apiUrl}/auth/register`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout() {
    return this.request(`${this.config.apiUrl}/auth/logout`, {
      method: 'POST',
    });
  }

  async refreshToken() {
    return this.request(`${this.config.apiUrl}/auth/refresh`, {
      method: 'POST',
    });
  }

  // Athlete APIs
  async getAthletes(page: number = 1, limit: number = 20, filters?: any) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return this.request(`${this.config.apiUrl}/athletes?${params}`);
  }

  async getAthlete(id: string) {
    return this.request(`${this.config.apiUrl}/athletes/${id}`);
  }

  async createAthlete(athleteData: any) {
    return this.request(`${this.config.apiUrl}/athletes`, {
      method: 'POST',
      body: JSON.stringify(athleteData),
    });
  }

  async updateAthlete(id: string, athleteData: any) {
    return this.request(`${this.config.apiUrl}/athletes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(athleteData),
    });
  }

  async uploadAthleteImage(id: string, imageFile: File) {
    const formData = new FormData();
    formData.append('file', imageFile);

    return fetch(`${this.config.apiUrl}/athletes/${id}/upload-image`, {
      method: 'POST',
      headers: {
        'Authorization': this.authToken ? `Bearer ${this.authToken}` : '',
      },
      body: formData,
    });
  }

  // Brand APIs
  async getBrands(page: number = 1, limit: number = 20, filters?: any) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return this.request(`${this.config.apiUrl}/brands?${params}`);
  }

  async getBrand(id: string) {
    return this.request(`${this.config.apiUrl}/brands/${id}`);
  }

  async createBrand(brandData: any) {
    return this.request(`${this.config.apiUrl}/brands`, {
      method: 'POST',
      body: JSON.stringify(brandData),
    });
  }

  async updateBrand(id: string, brandData: any) {
    return this.request(`${this.config.apiUrl}/brands/${id}`, {
      method: 'PUT',
      body: JSON.stringify(brandData),
    });
  }

  async getBrandAnalytics(id: string, days: number = 30) {
    return this.request(`${this.config.apiUrl}/brands/${id}/analytics?days=${days}`);
  }

  // Campaign APIs
  async getCampaigns(page: number = 1, limit: number = 20, filters?: any) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return this.request(`${this.config.apiUrl}/campaigns?${params}`);
  }

  async getCampaign(id: string) {
    return this.request(`${this.config.apiUrl}/campaigns/${id}`);
  }

  async createCampaign(campaignData: any) {
    return this.request(`${this.config.apiUrl}/campaigns`, {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  }

  async updateCampaign(id: string, campaignData: any) {
    return this.request(`${this.config.apiUrl}/campaigns/${id}`, {
      method: 'PUT',
      body: JSON.stringify(campaignData),
    });
  }

  async deleteCampaign(id: string) {
    return this.request(`${this.config.apiUrl}/campaigns/${id}`, {
      method: 'DELETE',
    });
  }

  // Deal APIs
  async getDeals(page: number = 1, limit: number = 20, filters?: any) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return this.request(`${this.config.apiUrl}/deals?${params}`);
  }

  async getDeal(id: string) {
    return this.request(`${this.config.apiUrl}/deals/${id}`);
  }

  async createDeal(dealData: any) {
    return this.request(`${this.config.apiUrl}/deals`, {
      method: 'POST',
      body: JSON.stringify(dealData),
    });
  }

  async updateDeal(id: string, dealData: any) {
    return this.request(`${this.config.apiUrl}/deals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(dealData),
    });
  }

  async updateDealStatus(id: string, status: string) {
    return this.request(`${this.config.apiUrl}/deals/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  // AI Matching APIs
  async findAthleteMatches(brandId: string, preferences?: any) {
    return this.request(`${this.config.apiUrl}/matching/find-athletes`, {
      method: 'POST',
      body: JSON.stringify({ brand_id: brandId, preferences }),
    });
  }

  async findBrandMatches(athleteId: string, preferences?: any) {
    return this.request(`${this.config.apiUrl}/matching/find-brands`, {
      method: 'POST',
      body: JSON.stringify({ athlete_id: athleteId, preferences }),
    });
  }

  async calculateCompatibility(athleteId: string, brandId: string) {
    return this.request(`${this.config.apiUrl}/matching/compatibility`, {
      method: 'POST',
      body: JSON.stringify({ athlete_id: athleteId, brand_id: brandId }),
    });
  }

  async getTrendingAthletes(sport?: string, limit: number = 10) {
    const params = new URLSearchParams();
    if (sport) params.append('sport', sport);
    params.append('limit', limit.toString());
    
    return this.request(`${this.config.apiUrl}/matching/trending?${params}`);
  }

  async getMarketInsights(sport?: string) {
    const params = sport ? `?sport=${sport}` : '';
    return this.request(`${this.config.apiUrl}/matching/market-insights${params}`);
  }

  // Analytics APIs
  async getPlatformAnalytics() {
    return this.request(`${this.config.apiUrl}/analytics/platform`);
  }

  async getUserAnalytics(userId: string) {
    return this.request(`${this.config.apiUrl}/analytics/user/${userId}`);
  }

  async getSportAnalytics(sport: string) {
    return this.request(`${this.config.apiUrl}/analytics/sport/${sport}`);
  }

  // Notification APIs
  async getNotifications(page: number = 1, limit: number = 20) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    return this.request(`${this.config.apiUrl}/notifications?${params}`);
  }

  async markNotificationRead(notificationId: string) {
    return this.request(`${this.config.apiUrl}/notifications/${notificationId}/read`, {
      method: 'PUT',
    });
  }

  async markAllNotificationsRead() {
    return this.request(`${this.config.apiUrl}/notifications/read-all`, {
      method: 'PUT',
    });
  }

  // File Upload APIs
  async uploadFile(file: File, context: string = 'general') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('context', context);

    return fetch(`${this.config.apiUrl}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': this.authToken ? `Bearer ${this.authToken}` : '',
      },
      body: formData,
    });
  }

  // AI Engine APIs (Direct)
  async getAIRecommendations(userId: string, userType: 'athlete' | 'brand') {
    return this.request(`${this.config.aiApiUrl}/recommendations`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, user_type: userType }),
    });
  }

  async trainAIModel(trainingData: any) {
    return this.request(`${this.config.aiApiUrl}/train`, {
      method: 'POST',
      body: JSON.stringify(trainingData),
    });
  }

  async getModelPerformance() {
    return this.request(`${this.config.aiApiUrl}/performance`);
  }
}

// Create and export singleton instance
export const apiClient = new APIClient();
export default apiClient;