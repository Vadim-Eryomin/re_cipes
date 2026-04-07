import * as t from 'io-ts'
import { DatetimeC, importDatetime } from './datetime'
import { type Record } from '../models/record'

export const RecordC = t.type(
  {
    id: t.string,
    created_at: DatetimeC,
    updated_at: t.union([DatetimeC, t.null, t.undefined]),
  },
  'RecordC',
)

export type RecordExternal = t.TypeOf<typeof RecordC>

export const importRecord = (input: RecordExternal): Record => {
  return {
    id: input.id,
    created_at: importDatetime(input.created_at),
    updated_at: input.updated_at ? importDatetime(input.updated_at) : null,
  }
}
