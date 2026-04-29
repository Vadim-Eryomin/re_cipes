import { UserTokens, UserRecord } from "../models/user"

export interface UserLoginReq {
  login: string
  password: string
}

export interface UserSignupReq {
  login: string
  password: string
  name: string
}

export interface UsersRepository {
  login(request: UserLoginReq): Promise<UserTokens>
  signup(request: UserSignupReq): Promise<void>
  getMyProfile(): Promise<UserRecord>
}
