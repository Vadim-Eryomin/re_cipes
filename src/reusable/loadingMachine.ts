import { createMachine, assign, fromPromise, type DoneActorEvent } from "xstate"

export interface LoadingContext<Q, D> {
  query: Q
  data?: D
  error?: unknown
}

export type LoadingEvent<Q> =
  | { type: 'LOAD' }
  | { type: 'RELOAD' }
  | { type: 'CHANGE_QUERY', query: Partial<Q> }

export function createLoadingMachine<Q extends object, D>(
  initialQuery: Q,
  loadData: (query: Q) => Promise<D>
) {
  return createMachine({
    types: {} as {
      context: LoadingContext<Q, D>
      events: LoadingEvent<Q>
    },

    initial: 'idle',

    context: {
      query: initialQuery,
      data: undefined,
      error: undefined,
    },

    states: {
      idle: {
        on: {
          LOAD: 'loading',
        },
      },
      loading: {
        invoke: {
          src: 'loadData',
          input: ({ context }) => context.query,
          onDone: {
            target: 'loaded',
            actions: assign({
              data: ({ event }) => event.output
            })
          },
          onError: {
            target: 'error',
          },
        },
      },
      loaded: {
        on: {
          RELOAD: 'loading',

          CHANGE_QUERY: {
            target: 'loading',
            guard: 'queryChanged',
            actions: assign({
              query: ({ context, event }) => ({
                ...context.query,
                ...event.query,
              })
            })
          }
        }
      },
      error: {
        on: {
          RELOAD: 'loading'
        },
      },
    }
  }, {
    actors: {
      loadData: fromPromise<D, Q>(async ({ input }) => {
        return loadData(input)
      })
    },
    guards: {
      queryChanged: ({ context, event }) => {
        if (event.type !== 'CHANGE_QUERY') return false

        return Object.entries(event.query).some(
          ([key, value]) => context.query[key as keyof Q] !== value
        )
      }
    },
  })
}
