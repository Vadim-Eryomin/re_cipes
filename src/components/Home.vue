<script lang="ts" setup>
import { Label } from '@nativescript/core';
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  $navigateTo,
  ActionBar,
} from 'nativescript-vue';
import RecipeMake from './Welcome.vue';

</script>

<template>
  <Frame>
    <Welcome />
    
  </Frame>
</template>

<!-- android-elevation & android-dynamic-elevation-offset: 0 -->
<style>
</style>