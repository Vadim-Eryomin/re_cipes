<template>
    <Page actionBarHidden="true" class="bg-[#13131A]">
        <FlexboxLayout class="flex-col justify-center items-center h-full">
            <Label text="Экран-заглушка" class="text-white text-2xl font-bold mb-4" />
            <Label text="Скоро здесь будет контент" class="text-gray-400 text-lg mb-8" />
            <Button text="Назад" 
                   class="bg-[#964BDC] text-white px-8 py-3 rounded-lg"
                   @tap="goBack" />
        </FlexboxLayout>
    </Page>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';

export default defineComponent({
    methods: {
        goBack(): void {
            this.$navigateBack();
        }
    }
});
</script>