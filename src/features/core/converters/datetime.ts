import { parseISO, formatISO } from 'date-fns/fp'
import * as t from 'io-ts'

export const DatetimeC = t.string
export type DatetimeExternal = t.TypeOf<typeof DatetimeC>

export const importDatetime = (input: DatetimeExternal) => {
  return parseISO(input)
}

export const exportDatetime = (date: Date) => {
  return formatISO(date)
}
