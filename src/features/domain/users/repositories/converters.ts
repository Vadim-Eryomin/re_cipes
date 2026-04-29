import * as t from 'io-ts'
import { importRecord, RecordC } from '~/features/core/converters/record'
import { UserRecord } from '../models/user'

export const UserC = t.type({
  name: t.string,
  avatar_url: t.union([t.string, t.null]),
  bio: t.union([t.string, t.null]),
})

export const UserRecordC = t.intersection([
  UserC,
  RecordC,
])

export type UserRecordExternal = t.TypeOf<typeof UserRecordC>

export const importUser = (input: UserRecordExternal): UserRecord => {
  return {
    ...importRecord(input),
    name: input.name,
    avatarUrl: input.avatar_url,
    bio: input.bio,
  }
}
