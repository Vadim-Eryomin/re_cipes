import { AjaxService } from '~/features/core/ajaxService'
import { PostsRepository, CreatePostRequest, UpdatePostRequest } from './interface'
import { Post } from '../models/post'
import { Comment } from '../models/comment'
import { PostC, importPost, CommentC, importComment } from './comment'
import * as t from 'io-ts'

export class PostsApiRepository implements PostsRepository {
  private ajaxService: AjaxService
  private baseUrl = '/posts'

  constructor({ ajaxService }: { ajaxService: AjaxService }) {
    this.ajaxService = ajaxService
  }

  async getFeed(limit: number, offset: number): Promise<Post[]> {
    const data = await this.ajaxService.get({
      url: `${this.baseUrl}/feed`,
      params: { limit, offset },
    })
    const posts = t.array(PostC).decode(data)
    if (posts._tag === 'Left') throw new Error('Invalid posts data')
    return posts.right.map(importPost)
  }

  async getMyPosts(limit: number, offset: number): Promise<Post[]> {
    const data = await this.ajaxService.get({
      url: `${this.baseUrl}/me`,
      params: { limit, offset },
    })
    const posts = t.array(PostC).decode(data)
    if (posts._tag === 'Left') throw new Error('Invalid posts data')
    return posts.right.map(importPost)
  }

  async getPost(postId: string): Promise<Post> {
    const data = await this.ajaxService.get({ url: `${this.baseUrl}/${postId}` })
    const post = PostC.decode(data)
    if (post._tag === 'Left') throw new Error('Invalid post data')
    return importPost(post.right)
  }

  async createPost(data: CreatePostRequest): Promise<Post> {
    const resp = await this.ajaxService.post({
      url: this.baseUrl,
      data,
    })
    const post = PostC.decode(resp)
    if (post._tag === 'Left') throw new Error('Invalid post data')
    return importPost(post.right)
  }

  async updatePost(postId: string, data: UpdatePostRequest): Promise<Post> {
    const resp = await this.ajaxService.put({
      url: `${this.baseUrl}/${postId}`,
      data,
    })
    const post = PostC.decode(resp)
    if (post._tag === 'Left') throw new Error('Invalid post data')
    return importPost(post.right)
  }

  async deletePost(postId: string): Promise<void> {
    await this.ajaxService.delete({ url: `${this.baseUrl}/${postId}` })
  }

  async likePost(postId: string): Promise<void> {
    await this.ajaxService.post({ url: `${this.baseUrl}/${postId}/like` })
  }

  async unlikePost(postId: string): Promise<void> {
    await this.ajaxService.delete({ url: `${this.baseUrl}/${postId}/like` })
  }

  async getComments(postId: string): Promise<Comment[]> {
    const data = await this.ajaxService.get({ url: `${this.baseUrl}/${postId}/comments` })
    const comments = t.array(CommentC).decode(data)
    if (comments._tag === 'Left') throw new Error('Invalid comments data')
    return comments.right.map(importComment)
  }

  async addComment(postId: string, text: string): Promise<Comment> {
    const data = await this.ajaxService.post({
      url: `${this.baseUrl}/${postId}/comments`,
      data: { text },
    })
    const comment = CommentC.decode(data)
    if (comment._tag === 'Left') throw new Error('Invalid comment data')
    return importComment(comment.right)
  }
}
