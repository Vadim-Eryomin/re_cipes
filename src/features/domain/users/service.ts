import { UserLoginReq, UserSignupReq, UsersRepository } from "./repositories/interface"
import { UserRecord } from "./models/user"

export class UsersService {
  private repository: UsersRepository

  constructor ({ repository }: { repository: UsersRepository }) {
    this.repository = repository
  }

  public login(request: UserLoginReq) {
    return this.repository.login(request)
  }
  
  public signup(request: UserSignupReq) {
    return this.repository.signup(request)
  }

  public getMyProfile(): Promise<UserRecord> {
    return this.repository.getMyProfile()
  }
}
