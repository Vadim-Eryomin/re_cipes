import { Post } from '../models/post'
import { Comment } from '../models/comment'

export interface CreatePostRequest {
  text: string
  recipe?: { step: string; media?: string }[]
  ingredients?: { name: string; count: number; measure_name: string }[]
  medias?: string[]
  disable_comments?: boolean
}

export interface UpdatePostRequest {
  text?: string
  recipe?: { step: string; media?: string }[]
  ingredients?: { name: string; count: number; measure_name: string }[]
  medias?: string[]
  disable_comments?: boolean
}

export interface PostsRepository {
  getFeed(limit: number, offset: number): Promise<Post[]>
  getMyPosts(limit: number, offset: number): Promise<Post[]>
  getPost(postId: string): Promise<Post>
  createPost(data: CreatePostRequest): Promise<Post>
  updatePost(postId: string, data: UpdatePostRequest): Promise<Post>
  deletePost(postId: string): Promise<void>
  likePost(postId: string): Promise<void>
  unlikePost(postId: string): Promise<void>
  getComments(postId: string): Promise<Comment[]>
  addComment(postId: string, text: string): Promise<Comment>
}
