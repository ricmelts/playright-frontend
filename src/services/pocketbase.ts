/**
 * PocketBase Client Service
 * Direct integration with PocketBase for real-time features
 */

import PocketBase, { RecordService } from 'pocketbase';

class PocketBaseClient {
  public pb: PocketBase;

  constructor() {
    const url = process.env.REACT_APP_POCKETBASE_URL || 'http://localhost:8090';
    this.pb = new PocketBase(url);
  }

  // Authentication
  async login(email: string, password: string) {
    return await this.pb.collection('users').authWithPassword(email, password);
  }

  async register(email: string, password: string, data: any) {
    return await this.pb.collection('users').create({
      email,
      password,
      passwordConfirm: password,
      ...data,
    });
  }

  async logout() {
    this.pb.authStore.clear();
  }

  isAuthenticated() {
    return this.pb.authStore.isValid;
  }

  getCurrentUser() {
    return this.pb.authStore.model;
  }

  getAuthToken() {
    return this.pb.authStore.token;
  }

  // Real-time subscriptions
  async subscribeToCollection(
    collection: string,
    callback: (data: any) => void,
    filter?: string
  ) {
    return await this.pb.collection(collection).subscribe('*', callback, filter);
  }

  async unsubscribe(collection?: string) {
    if (collection) {
      this.pb.collection(collection).unsubscribe();
    } else {
      this.pb.unsubscribe();
    }
  }

  // Collection helpers
  athletes() {
    return this.pb.collection('athletes');
  }

  brands() {
    return this.pb.collection('brands');
  }

  campaigns() {
    return this.pb.collection('campaigns');
  }

  deals() {
    return this.pb.collection('deals');
  }

  matches() {
    return this.pb.collection('matches');
  }

  notifications() {
    return this.pb.collection('notifications');
  }

  users() {
    return this.pb.collection('users');
  }

  athleteMetrics() {
    return this.pb.collection('athlete_metrics');
  }

  // Real-time hooks for React components
  useRealtime(collection: string, callback: (data: any) => void, deps: any[] = []) {
    const { useEffect } = require('react');
    
    useEffect(() => {
      let unsubscribe: any;

      const subscribe = async () => {
        unsubscribe = await this.subscribeToCollection(collection, callback);
      };

      subscribe();

      return () => {
        if (unsubscribe) {
          unsubscribe();
        }
      };
    }, deps);
  }

  // File upload helper
  async uploadFile(file: File, collection: string, recordId: string, fieldName: string) {
    const formData = new FormData();
    formData.append(fieldName, file);

    return await this.pb.collection(collection).update(recordId, formData);
  }

  // Utility methods
  getFileUrl(record: any, filename: string) {
    return this.pb.getFileUrl(record, filename);
  }

  async getRecordById(collection: string, id: string, expand?: string) {
    try {
      return await this.pb.collection(collection).getOne(id, { expand });
    } catch (error) {
      console.error(`Error fetching ${collection} record ${id}:`, error);
      throw error;
    }
  }

  async getRecords(
    collection: string,
    page: number = 1,
    perPage: number = 20,
    filter?: string,
    sort?: string,
    expand?: string
  ) {
    try {
      return await this.pb.collection(collection).getList(page, perPage, {
        filter,
        sort,
        expand,
      });
    } catch (error) {
      console.error(`Error fetching ${collection} records:`, error);
      throw error;
    }
  }

  async createRecord(collection: string, data: any) {
    try {
      return await this.pb.collection(collection).create(data);
    } catch (error) {
      console.error(`Error creating ${collection} record:`, error);
      throw error;
    }
  }

  async updateRecord(collection: string, id: string, data: any) {
    try {
      return await this.pb.collection(collection).update(id, data);
    } catch (error) {
      console.error(`Error updating ${collection} record ${id}:`, error);
      throw error;
    }
  }

  async deleteRecord(collection: string, id: string) {
    try {
      return await this.pb.collection(collection).delete(id);
    } catch (error) {
      console.error(`Error deleting ${collection} record ${id}:`, error);
      throw error;
    }
  }
}

// Create and export singleton instance
export const pbClient = new PocketBaseClient();
export default pbClient;