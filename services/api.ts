import { Http, HttpResponse } from '@nativescript/core';

export const BASE_URL = 'http://10.0.2.2:5000';

export function mediaUrl(path: string | null | undefined): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('~/')) {
    return path;
  }
  const normalized = path.replace(/\\/g, '/');
  const urlPath = normalized.startsWith('/') ? normalized : `/${normalized}`;
  return BASE_URL + urlPath;
}

class ApiService {
  private token: string = '';

  constructor() {
    const { ApplicationSettings } = require('@nativescript/core');
    this.token = ApplicationSettings.getString('token', '');
  }

  getToken(): string {
    return this.token;
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

  private getHeaders(contentType = 'application/json'): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': contentType,
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async parseResponse(response: HttpResponse): Promise<any> {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.content) {
        return response.content.toJSON();
      }
      return {};
    }

    const errorData = response.content ? response.content.toJSON() : {};
    throw { response: { status: response.statusCode, data: errorData } };
  }

  async get(url: string): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'GET',
        headers: this.getHeaders(),
      });
      return this.parseResponse(response);
    } catch (error) {
      console.error('GET request failed:', error);
      throw error;
    }
  }

  async post(url: string, data?: any): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'POST',
        headers: this.getHeaders(),
        content: data ? JSON.stringify(data) : undefined,
      });
      return this.parseResponse(response);
    } catch (error) {
      console.error('POST request failed:', error);
      throw error;
    }
  }

  async patch(url: string, data: any): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'PATCH',
        headers: this.getHeaders(),
        content: JSON.stringify(data),
      });
      return this.parseResponse(response);
    } catch (error) {
      console.error('PATCH request failed:', error);
      throw error;
    }
  }

  async put(url: string, data: any): Promise<any> {
    try {
      const response: HttpResponse = await Http.request({
        url: BASE_URL + url,
        method: 'PUT',
        headers: this.getHeaders(),
        content: JSON.stringify(data),
      });
      return this.parseResponse(response);
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
        headers: this.getHeaders(),
      });
      return this.parseResponse(response);
    } catch (error) {
      console.error('DELETE request failed:', error);
      throw error;
    }
  }

  // --- Auth ---
  login(login: string, password: string) {
    return this.post('/login', { login, password });
  }

  register(name: string, login: string, password: string) {
    return this.post('/register', { name, login, password });
  }

  // --- Users ---
  getMe() {
    return this.get('/users/me');
  }

  updateMe(data: { name?: string; login?: string; password?: string; image_id?: number }) {
    return this.patch('/users/me', data);
  }

  deleteMe() {
    return this.delete('/users/me');
  }

  // --- Threads ---
  listThreads(q?: string) {
    const query = q ? `?q=${encodeURIComponent(q)}` : '';
    return this.get(`/threads${query}`);
  }

  createThread(title: string) {
    return this.post('/threads', { title });
  }

  async findOrCreateThread(title: string) {
    const formatted = title.trim().toLowerCase().startsWith('r/')
      ? title.trim()
      : `r/${title.trim()}`;

    const threads = await this.listThreads(formatted.replace(/^r\//, ''));
    const existing = (threads as any[]).find(
      (t) => t.title.toLowerCase() === formatted.toLowerCase()
    );
    if (existing) return existing;

    return this.createThread(formatted);
  }

  // --- Recipes ---
  listRecipes(page = 1, perPage = 50, threadId?: number) {
    let url = `/recipes?page=${page}&per_page=${perPage}`;
    if (threadId) url += `&thread_id=${threadId}`;
    return this.get(url);
  }

  myRecipes(page = 1, perPage = 50) {
    return this.get(`/recipes/me?page=${page}&per_page=${perPage}`);
  }

  getRecipe(recipeId: string | number) {
    return this.get(`/recipes/${recipeId}`);
  }

  createRecipe(data: {
    title: string;
    thread_id: number;
    description?: string;
    main_image_id?: number;
    ingredients: { name: string; quantity: string; unit: string }[];
    steps: { order_index: number; description: string; image_id?: number }[];
  }) {
    return this.post('/recipes', data);
  }

  updateRecipe(
    recipeId: string | number,
    data: {
      title?: string;
      description?: string;
      thread_id?: number;
      main_image_id?: number | null;
      ingredients?: { name: string; quantity: string; unit: string }[];
      steps?: { order_index: number; description: string; image_id?: number }[];
    }
  ) {
    return this.patch(`/recipes/${recipeId}`, data);
  }

  deleteRecipe(recipeId: string | number) {
    return this.delete(`/recipes/${recipeId}`);
  }

  voteRecipe(recipeId: string | number, action: 'up' | 'down') {
    return this.post(`/recipes/${recipeId}/vote`, { action });
  }

  // --- Comments ---
  getComments(recipeId: string | number, page = 1, perPage = 100) {
    return this.get(`/recipes/${recipeId}/comments?page=${page}&per_page=${perPage}`);
  }

  addComment(recipeId: string | number, content: string, parentId?: number) {
    const body: { content: string; parent_id?: number } = { content };
    if (parentId) body.parent_id = parentId;
    return this.post(`/recipes/${recipeId}/comments`, body);
  }
}

export default new ApiService();
