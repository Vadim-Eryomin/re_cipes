import { createApp } from 'nativescript-vue';
import App from './App.vue';

import AbortControllerPolyfill from 'abort-controller'

if (!globalThis.AbortController) {
  globalThis.AbortController = AbortControllerPolyfill as unknown as typeof AbortController
}

createApp(App).start();