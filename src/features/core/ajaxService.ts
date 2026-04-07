import { request } from '@nativescript/core/http'
import { secureStorage } from '~/init/storage'

interface RequestOptions<T = any> {
  url: string
  data?: T
  params?: Record<string, any>
}

export class AjaxService {
  private _baseURL: string
  private _refreshPromise: Promise<void> | null = null

  constructor(baseURL: string) {
    this._baseURL = baseURL
  }

  private getAuthHeader() {
    const accessToken = secureStorage.getSync({ key: 'accessToken' })

    if (accessToken) {
      return `Bearer ${accessToken}`
    }

    return ''
  }

  private buildUrl(url: string, params?: Record<string, any>) {
    if (!params) {
      return this._baseURL + url
    }

    const search = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        search.append(key, String(value))
      }
    })

    return `${this._baseURL + url}?${search.toString()}`
  }

  private async refreshToken() {
    if (this._refreshPromise) {
      return this._refreshPromise
    }

    this._refreshPromise = (async () => {
      const refreshToken = secureStorage.getSync({ key: 'refreshToken' })

      if (!refreshToken) {
        throw new Error('No refresh token')
      }

      const resp = await request({
        url: this._baseURL + '/users/refresh',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        content: JSON.stringify({ refresh_token: refreshToken })
      })

      const data = resp.content?.toJSON()

      secureStorage.setSync({
        key: 'accessToken',
        value: data.access_token
      })

      if (data.refresh_token) {
        secureStorage.setSync({
          key: 'refreshToken',
          value: data.refresh_token
        })
      }
    })()

    try {
      await this._refreshPromise
    } finally {
      this._refreshPromise = null
    }
  }

  private async _request(method: string, { url, data, params }: RequestOptions) {
    const makeRequest = async () => {
      const fullUrl = this.buildUrl(url, params)

      const resp = await request({
        url: fullUrl,
        method,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: this.getAuthHeader(),
        },
        content: data ? JSON.stringify(data) : undefined
      })

      return resp
    }

    let resp = await makeRequest()

    if (resp.statusCode === 401) {
      await this.refreshToken()
      resp = await makeRequest()
    }

    return resp.content?.toJSON()
  }

  public get(options: RequestOptions) {
    return this._request('GET', options)
  }

  public post(options: RequestOptions) {
    return this._request('POST', options)
  }

  public put(options: RequestOptions) {
    return this._request('PUT', options)
  }

  public patch(options: RequestOptions) {
    return this._request('PATCH', options)
  }

  public delete(options: RequestOptions) {
    return this._request('DELETE', options)
  }
}
