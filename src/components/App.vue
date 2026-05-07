<template>
  <Frame id="root-frame">
    <Login />
  </Frame>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';
import Login from './Login.vue';

export default defineComponent({
  components: {
    Login,
  },
});
</script>