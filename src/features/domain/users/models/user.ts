import { Record } from "~/features/core/models/record"

export interface UserTokens {
  access_token: string
  refresh_token: string
}

export interface User {
  name: string
  avatarUrl: string | null
  bio: string | null
}

export interface UserRecord extends User, Record {}
