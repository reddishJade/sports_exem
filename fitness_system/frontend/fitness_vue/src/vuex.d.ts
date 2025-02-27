import { Store } from 'vuex'

declare module '@vue/runtime-core' {
  interface State {
    token: string
  }

  interface ComponentCustomProperties {
    $store: Store<State>
  }
}

export {}
