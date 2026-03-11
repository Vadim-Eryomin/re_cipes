<template>
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
</template>

<script lang="ts" setup>
import { ref } from 'nativescript-vue';
import { $navigateTo } from 'nativescript-vue';
import Login from './Login.vue';

const onPageLoaded = (): void => {
    console.log('Welcome page loaded');
};

const goToLogin = (): void => {
    console.log('Navigating to Login');
    $navigateTo(Login, {
        transition: {
            name: 'fade',
            duration: 300
        }
    });
};
</script>