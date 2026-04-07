import * as t from 'io-ts'
import { importRecord, RecordC } from '~/features/core/converters/record'
import { importDatetime, DatetimeC } from '~/features/core/converters/datetime'
import { Post } from '../models/post'
import { Comment } from '../models/comment'

const AuthorC = t.type({
  id: t.string,
  name: t.string,
  avatar_url: t.union([t.string, t.null]),
})
export type AuthorExternal = t.TypeOf<typeof AuthorC>

const RecipeStepC = t.type({
  step: t.string,
  media: t.union([t.string, t.null]),
})

const IngredientC = t.type({
  name: t.string,
  count: t.number,
  measure_name: t.string,
})

export const PostC = t.type({
  id: t.string,
  text: t.string,
  community: t.union([t.string, t.null]),
  recipe: t.union([t.array(RecipeStepC), t.null]),
  ingredients: t.union([t.array(IngredientC), t.null]),
  medias: t.array(t.string),
  disable_comments: t.boolean,
  author: AuthorC,
  likes_count: t.number,
  created_at: DatetimeC,
  updated_at: t.union([DatetimeC, t.null, t.undefined]),
});

export type PostExternal = t.TypeOf<typeof PostC>

export const CommentC = t.type({
  id: t.string,
  author: AuthorC,
  text: t.string,
  created_at: DatetimeC,
  updated_at: t.union([DatetimeC, t.null, t.undefined]),
})

export type CommentExternal = t.TypeOf<typeof CommentC>

export const importPost = (input: PostExternal): Post => {
  return {
    ...importRecord({
      id: input.id,
      created_at: input.created_at,
      updated_at: input.updated_at,
    }),
    text: input.text,
    community: input.community,
    recipe: input.recipe,
    ingredients: input.ingredients,
    medias: input.medias,
    disable_comments: input.disable_comments,
    author: input.author,
    likes_count: input.likes_count,
  }
}

export const importComment = (input: CommentExternal): Comment => {
  return {
    ...importRecord({
      id: input.id,
      created_at: input.created_at,
      updated_at: input.updated_at,
    }),
    author: input.author,
    text: input.text,
  }
}