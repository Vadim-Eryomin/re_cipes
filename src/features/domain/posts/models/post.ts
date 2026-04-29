import { Record } from '~/features/core/models/record'
import { Ingredient } from './ingredient'
import { RecipeStep } from './recipeStep'

export interface Author {
  id: string
  name: string
  avatar_url: string | null
}

export interface Post extends Record {
  text: string
  community: string | null   
  recipe: RecipeStep[] | null
  ingredients: Ingredient[] | null
  medias: string[]
  disable_comments: boolean
  author: Author
  likes_count: number
}
