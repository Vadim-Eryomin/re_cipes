import { AjaxService } from "~/features/core/ajaxService"
import { UserLoginReq, UserSignupReq, UsersRepository } from "./interface"
import { UserTokens, UserRecord } from "../models/user"
import { UserRecordC, importUser } from "./converters"

export class UsersApiRepository implements UsersRepository {
  private ajaxService: AjaxService
  private baseUrl = '/users'

  constructor ({ ajaxService }: { ajaxService: AjaxService }) {
    this.ajaxService = ajaxService
  }

  login(request: UserLoginReq): Promise<UserTokens> {
    return this.ajaxService.post({
      url: this.baseUrl + '/login',
      data: request,
    })
  }

  signup(request: UserSignupReq): Promise<void> {
    return this.ajaxService.post({
      url: this.baseUrl + '/signup',
      data: request,
    })
  }

  async getMyProfile(): Promise<UserRecord> {
    const data = await this.ajaxService.get({
      url: this.baseUrl + '/me'
    })
    const user = UserRecordC.decode(data)
    if (user._tag === 'Left') throw new Error('Invalid user data')
    return importUser(user.right)
  }
}
