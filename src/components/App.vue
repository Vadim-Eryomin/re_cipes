<template>
  <Frame id="root-frame">
    <Login />
  </Frame>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';
import Login from './Login.vue';
import { initFirebase } from '~/fcm';

export default defineComponent({
   mounted() {
    initFirebase().catch(console.error);
  },
  components: {
    Login,
  },
});
</script>