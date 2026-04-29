import { PostsRepository, CreatePostRequest, UpdatePostRequest } from './repositories/interface'
import { Post } from './models/post'
import { Comment } from './models/comment'

export class PostsService {
  private repository: PostsRepository

  constructor({ repository }: { repository: PostsRepository }) {
    this.repository = repository
  }

  getFeed(limit: number, offset: number): Promise<Post[]> {
    return this.repository.getFeed(limit, offset)
  }

  getMyPosts(limit: number, offset: number): Promise<Post[]> {
    return this.repository.getMyPosts(limit, offset)
  }

  getPost(postId: string): Promise<Post> {
    return this.repository.getPost(postId)
  }

  createPost(data: CreatePostRequest): Promise<Post> {
    return this.repository.createPost(data)
  }

  updatePost(postId: string, data: UpdatePostRequest): Promise<Post> {
    return this.repository.updatePost(postId, data)
  }

  deletePost(postId: string): Promise<void> {
    return this.repository.deletePost(postId)
  }

  likePost(postId: string): Promise<void> {
    return this.repository.likePost(postId)
  }

  unlikePost(postId: string): Promise<void> {
    return this.repository.unlikePost(postId)
  }

  getComments(postId: string): Promise<Comment[]> {
    return this.repository.getComments(postId)
  }

  addComment(postId: string, text: string): Promise<Comment> {
    return this.repository.addComment(postId, text)
  }
}
