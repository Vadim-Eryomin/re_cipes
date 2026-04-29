import { Record } from '~/features/core/models/record'
import { Author } from './post'

export interface Comment extends Record {
  author: Author
  text: string
}
