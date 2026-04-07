import { createApp } from 'nativescript-vue';
import Home from './components/Home.vue';

import { init } from '@nativescript/background-http';
init()

createApp(Home).start();
