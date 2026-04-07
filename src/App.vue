<script lang="ts" setup>
import { secureStorage } from '~/init/storage'
import MainPage from './components/MainPage.vue';

secureStorage.setSync({
  key: 'accessToken',
  value: 'test-token-123'
})
</script>

<template>
  <Frame>
    <MainPage />
  </Frame>
</template>
