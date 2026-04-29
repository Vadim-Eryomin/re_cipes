import { createApp } from 'nativescript-vue';
import App from './App.vue';

import AbortControllerPolyfill from 'abort-controller'

import { init } from '@nativescript/background-http';
init()

if (!globalThis.AbortController) {
  globalThis.AbortController = AbortControllerPolyfill as unknown as typeof AbortController
}

createApp(App).start();