import { computed } from "nativescript-vue"
import { createMachine, fromPromise } from "xstate"
import { useMachine } from "@xstate/vue"

type AsyncActionMachineEvents<P> =
  | { type: 'INVOKE', payload: P }
  
export const useAsyncActionMachine = <P>({
  invoke,
  canInvoke = () => true,
  notifyError = () => {},
  notifySuccess = () => {},
}: {
  invoke: (payload: P) => Promise<void>
  canInvoke?: () => boolean
  notifyError?: () => void
  notifySuccess?: () => void
}) => {
  const machine = createMachine({
    types: {} as {
      events: AsyncActionMachineEvents<P>
      context: {}
    },
    initial: 'idle',
    states: {
      idle: {
        on: {
          INVOKE: {
            target: 'processing',
            guard: 'canInvoke',
          },
        },
      },
      processing: {
        invoke: {
          src: 'processor',
          input: ({ event }) => event.payload,
          onDone: {
            target: 'idle',
            actions: 'notifySuccess',
          },
          onError: {
            target: 'error',
            actions: 'notifyError',
          },
        },
      },
      error: {},
    },
  }, {
    actors: {
      processor: fromPromise<void, P>(async (data) => {
        await invoke(data.input)
      })
    },
    actions: {
      notifyError,
      notifySuccess,
    },
    guards: {
      canInvoke,
    },
  })

  const { snapshot: state, send } = useMachine(machine)

  return {
    isPending: computed(() => state.value.matches('processing')),
    isError: computed(() => state.value.matches('error')),
    invoke: (payload: P) => {
      send({ type: 'INVOKE', payload })
    },
  }
}
