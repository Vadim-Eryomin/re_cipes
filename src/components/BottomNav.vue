<template>
    <FlexboxLayout flexDirection="row" justifyContent="space-between" alignItems="center"
                   class="bg-[#121212] py-3 px-4 border-top"
                   @tap="preventClose">

        <StackLayout class="items-center" @tap="navigateTo('main')">
            <Image :src="activeTab === 'main' ? '~/assets/home-active.png' : '~/assets/home-inactive.png'"
                   width="26" height="26" />
            <Label text="Главный"
                   :class="['font-inter font-semibold text-[10px] mt-1 text-center', activeTab === 'main' ? 'text-[#F25C05]' : 'text-[#c7c7c7]']" />
        </StackLayout>

        <StackLayout class="items-center" @tap="navigateTo('create')">
            <Image :src="activeTab === 'create' ? '~/assets/create-active.png' : '~/assets/create-inactive.png'"
                   width="26" height="26" />
            <Label text="Создать"
                   :class="['font-inter font-semibold text-[10px] mt-1 text-center', activeTab === 'create' ? 'text-[#F25C05]' : 'text-[#c7c7c7]']" />
        </StackLayout>

        <StackLayout class="items-center" @tap="navigateTo('recipes')">
            <Image src="~/assets/logoMini.png"
                   width="36" height="36" />
        </StackLayout>

        <StackLayout class="items-center" @tap="navigateTo('topics')">
            <Image :src="activeTab === 'topics' ? '~/assets/topics-active.png' : '~/assets/topics-inactive.png'"
                   width="26" height="26" />
            <Label text="Мои топики"
                   :class="['font-inter font-semibold text-[10px] mt-1 text-center', activeTab === 'topics' ? 'text-[#F25C05]' : 'text-[#c7c7c7]']" />
        </StackLayout>

        <StackLayout class="items-center" @tap="navigateTo('profile')">
            <Image :src="activeTab === 'profile' ? '~/assets/profile-active.png' : '~/assets/profile-inactive.png'"
                   width="26" height="26" />
            <Label text="Профиль"
                   :class="['font-inter font-semibold text-[10px] mt-1 text-center', activeTab === 'profile' ? 'text-[#F25C05]' : 'text-[#c7c7c7]']" />
        </StackLayout>

    </FlexboxLayout>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';
import RecipeMake from './RecipeMake.vue';
import Profile from './Profile.vue';
import TopicCreate from './TopicCreate.vue';
import MainPage from './MainPage.vue';

export default defineComponent({
    props: {
        activeTab: {
            type: String,
            default: 'main'
        }
    },
    methods: {
        navigateTo(tab: string): void {
            this.$emit('update:activeTab', tab);

            switch(tab) {
                case 'create':
                    this.$navigateTo(RecipeMake, {
                        transition: { name: 'fade', duration: 300 }
                    });
                    break;
                case 'profile':
                    this.$navigateTo(Profile, {
                        transition: { name: 'fade', duration: 300 }
                    });
                    break;
                case 'main':
                    this.$navigateTo(MainPage, {
                        transition: { name: 'fade', duration: 300 }
                    });
                    break;
                    break;
                case 'recipes':
                    console.log('ReCipes');
                    break;
                case 'topics':
                    this.$navigateTo(TopicCreate, {
                        transition: { name: 'fade', duration: 300 }
                    });
                    break;
            }
        },

        preventClose(): void {
        }
    }
});
</script>

<style scoped>
.border-top {
    border-top-width: 1;
    border-top-color: #5b5858;
}
</style>