import { ajaxService } from './ajax'
import { UsersApiRepository } from '~/features/domain/users/repositories/api'
import { UsersService } from '~/features/domain/users/service'
import { PostsApiRepository } from '~/features/domain/posts/repositories/api'
import { PostsService } from '~/features/domain/posts/service'

const usersService = new UsersService({
  repository: new UsersApiRepository({ ajaxService })
})

const postsService = new PostsService({
  repository: new PostsApiRepository({ ajaxService })
})

export {
  usersService,
  postsService,
}