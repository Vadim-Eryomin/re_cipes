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
import RecipeMake from './RecipeMake.vue';

</script>

<template>
  <Frame>
    <RecipeMake />
    
  </Frame>
</template>

<!-- android-elevation & android-dynamic-elevation-offset: 0 -->
<style>
</style>
