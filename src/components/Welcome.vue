<template>
    <Page actionBarHidden="true">
        <GridLayout
            rows="*"
            columns="*"
            backgroundColor="#F25C05"
        >
            <Image
                src="~/assets/splash_logo.png"
                width="60%"
                stretch="aspectFit"
                horizontalAlignment="center"
                verticalAlignment="center"
            />
        </GridLayout>
    </Page>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';

export default defineComponent({
});
</script>
