import { createApp } from 'nativescript-vue';
import App from './components/App.vue';
import AbortControllerPolyfill from 'abort-controller'
import { initFirebase } from './fcm';

initFirebase().catch(console.error);

if (!globalThis.AbortController) {
  globalThis.AbortController = AbortControllerPolyfill as unknown as typeof AbortController
}

createApp(App).start();