import { Http, HttpResponse } from '@nativescript/core';

const BASE_URL = 'http://10.0.2.2:5000';

class ApiService {
  private token: string = '';

  constructor() {
    const { ApplicationSettings } = require('@nativescript/core');
    this.token = ApplicationSettings.getString('token', '');
  }

  setToken(token: string) {
    this.token = token;
    const { ApplicationSettings } = require('@nativescript/core');
    ApplicationSettings.setString('token', token);
  }

  clearToken() {
    this.token = '';
    const { ApplicationSettings } = require('@nativescript/core');
    ApplicationSettings.remove('token');
  }

  private getHeaders(): any {
    const headers: any = {
      'Content-Type': 'application/json'
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async get(url: string): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'GET',
        headers: this.getHeaders()
      });
      
      if (response.statusCode >= 200 && response.statusCode < 300 && response.content) {
        return response.content.toJSON();
      } else if (response.statusCode >= 200 && response.statusCode < 300) {
        return {};
      } else {
        throw new Error(`HTTP ${response.statusCode}`);
      }
    } catch (error) {
      console.error('GET request failed:', error);
      throw error;
    }
  }

  async post(url: string, data: any): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'POST',
        headers: this.getHeaders(),
        content: JSON.stringify(data)
      });
      
      if (response.statusCode >= 200 && response.statusCode < 300 && response.content) {
        return response.content.toJSON();
      } else if (response.statusCode >= 200 && response.statusCode < 300) {
        return {};
      } else {
        const errorData = response.content ? response.content.toJSON() : {};
        throw { response: { status: response.statusCode, data: errorData } };
      }
    } catch (error) {
      console.error('POST request failed:', error);
      throw error;
    }
  }

  async put(url: string, data: any): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'PUT',
        headers: this.getHeaders(),
        content: JSON.stringify(data)
      });
      
      if (response.statusCode >= 200 && response.statusCode < 300 && response.content) {
        return response.content.toJSON();
      } else if (response.statusCode >= 200 && response.statusCode < 300) {
        return {};
      } else {
        throw new Error(`HTTP ${response.statusCode}`);
      }
    } catch (error) {
      console.error('PUT request failed:', error);
      throw error;
    }
  }

  async delete(url: string): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'DELETE',
        headers: this.getHeaders()
      });
      
      if (response.statusCode >= 200 && response.statusCode < 300 && response.content) {
        return response.content.toJSON();
      } else if (response.statusCode >= 200 && response.statusCode < 300) {
        return {};
      } else {
        throw new Error(`HTTP ${response.statusCode}`);
      }
    } catch (error) {
      console.error('DELETE request failed:', error);
      throw error;
    }
  }
}

export default new ApiService();