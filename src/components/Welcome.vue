<template>
  <Frame id="root-frame">
    <Page actionBarHidden="true" @loaded="onPageLoaded">
      <FlexboxLayout 
        class="flex-col justify-start items-center h-full bg-[#F25C05]"
        @tap="goToLogin"
      >
        <StackLayout class="h-[30%]" />
      
        <Image
          src="~/assets/logo.png"
          class="w-[55%]"
          stretch="aspectFit"
        />
      </FlexboxLayout>
    </Page>
  </Frame>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';
import Login from './Login.vue';

export default defineComponent({
  methods: {
    onPageLoaded() {
      console.log('Welcome page loaded');
    },

    goToLogin() {
      console.log('Navigating to Login');
      this.$navigateTo(Login, {
        transition: {
          name: 'fade',
          duration: 120
        }
      });
    }
  }
});
</script>