<script lang="ts" setup>
import { 
    GridLayout, 
    Image, 
    Label, 
    ScrollView, 
    StackLayout, 
    TextField, 
    TextView, 
    Button,
    FlexboxLayout,
    Switch
} from '@nativescript/core';
import { Dialogs } from '@nativescript/core';
import { ref } from "nativescript-vue";
import { $navigateTo } from 'nativescript-vue';
import BottomNav from './BottomNav.vue';
import MainPage from './MainPage.vue';

const topicName = ref('')
const topicDescription = ref('')
const isPrivate = ref(true)
const isLoading = ref(false)
const activeTab = ref('topics')
const error = ref('')

const MAX_TOPIC_LENGTH = 30
const MIN_TOPIC_LENGTH = 3

function validateTopicName(name: string): boolean {
    const validPattern = /^[a-zA-Z0-9_\-\/\u0400-\u04FF\s]+$/
    return validPattern.test(name) && name.length >= MIN_TOPIC_LENGTH && name.length <= MAX_TOPIC_LENGTH
}

function formatTopicName(name: string): string {
    let formatted = name.trim()
    if (!formatted.startsWith('r/') && !formatted.startsWith('R/')) {
        formatted = 'r/' + formatted
    }
    return formatted
}

function onPublicSwitchChange(args: any) {
    const sw = args.object as Switch;
    if (sw.checked) {
        isPrivate.value = false;
    }
}

function onPrivateSwitchChange(args: any) {
    const sw = args.object as Switch;
    if (sw.checked) {
        isPrivate.value = true;
    }
}

async function createTopic() {
    error.value = ''
    
    if (!topicName.value.trim()) {
        error.value = 'Введите название топика'
        return
    }
    
    if (!validateTopicName(topicName.value)) {
        error.value = `Название должно быть от ${MIN_TOPIC_LENGTH} до ${MAX_TOPIC_LENGTH} символов и содержать только буквы, цифры, _, -, /`
        return
    }
    
    const formattedName = formatTopicName(topicName.value)
    const confirm = await Dialogs.confirm({
        title: 'Создание топика',
        message: `Вы действительно хотите создать топик "${formattedName}"?`,
        okButtonText: 'Создать',
        cancelButtonText: 'Отмена'
    })
    
    if (!confirm) return
    
    isLoading.value = true
    
    setTimeout(() => {
        isLoading.value = false
        Dialogs.alert({
            title: 'Успешно',
            message: `Топик "${formattedName}" создан`,
            okButtonText: 'OK'
        }).then(() => {
            $navigateTo(MainPage, {
                props: { initialTopic: formattedName },
                transition: { name: "slideLeft" },
                clearHistory: false
            })
        })
    }, 1000)
}

function onTopicNameChange(args: any) {
    error.value = ''
}
</script>

<template>
    <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
        <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
            
            <ScrollView row="0" col="0">
                <FlexboxLayout flexDirection="column" alignItems="stretch" class="px-4 pt-12 pb-24">
                    
                    <Label text="Создать топик" class="text-[#F25C05] text-lg font-bold mb-6 text-left" textWrap="true" />

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Что такое топик?" class="text-white font-bold text-[14px] mb-2" />
                        <Label text="Топик — это тематическая категория для ваших рецептов. Например: r/выпечка, r/завтраки, r/веганские_блюда" 
                            class="text-[#C7C7C7] text-[12px]" textWrap="true" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Название топика *" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <TextField v-model="topicName" 
                            :hint="'r/ваш_топик'" 
                            @textChange="onTopicNameChange"
                            class="bg-[#121212] text-white rounded-xl px-3 py-2 text-[14px]" />
                        <Label :text="`${topicName.length}/${MAX_TOPIC_LENGTH}`" 
                            class="text-[#C7C7C7] text-[10px] text-right mt-1" />
                        <Label v-if="error" :text="error" 
                            class="text-[#FF4444] text-[12px] mt-2" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Описание (необязательно)" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <TextView v-model="topicDescription" 
                            :hint="'О чём этот топик? Расскажите подробнее...'" 
                            class="bg-[#121212] text-white rounded-xl p-3 text-[14px]" 
                            :height="100" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Настройки доступа" class="text-white font-bold text-[14px] mb-3" />
                        
                        <FlexboxLayout flexDirection="row" alignItems="center" class="mb-3">
                            <StackLayout width="75%">
                                <Label text="Публичный топик" class="text-white text-[14px]" />
                                <Label text="Любой пользователь может публиковать рецепты" textWrap="true"
                                    class="text-[#C7C7C7] text-[12px]" />
                            </StackLayout>
                            <Switch :checked="!isPrivate" @checkedChange="onPublicSwitchChange" class="switch-primary" />
                        </FlexboxLayout>
                        
                        <GridLayout height="1" backgroundColor="#393939" class="my-2" />
                        
                        <FlexboxLayout flexDirection="row" alignItems="center" class="mb-3">
                            <StackLayout width="75%">
                                <Label text="Приватный топик" class="text-white text-[14px]" />
                                <Label text="Только вы можете публиковать рецепты" textWrap="true"
                                    class="text-[#C7C7C7] text-[12px]" />
                            </StackLayout>
                            <Switch :checked="isPrivate" @checkedChange="onPrivateSwitchChange" class="switch-primary" />
                        </FlexboxLayout>
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4" v-if="topicName">
                        <Label text="Предпросмотр" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <FlexboxLayout flexDirection="row" alignItems="center" class="bg-[#121212] rounded-xl p-3">
                            <Image src="~/assets/topic_icon.png" width="32" height="32" class="mr-3" />
                            <StackLayout>
                                <Label :text="formatTopicName(topicName)" 
                                    class="text-white font-bold text-[14px]" />
                                <Label :text="isPrivate ? '🔒 Приватный' : '🌍 Публичный'" 
                                    :class="['text-[12px]', isPrivate ? 'text-[#F25C05]' : 'text-[#479A0F]']" />
                            </StackLayout>
                        </FlexboxLayout>
                    </StackLayout>

                    <Button @tap="createTopic" :isEnabled="!isLoading"  textTransform="none"
                        :text="isLoading ? 'Создание...' : 'Создать топик'"
                        class="bg-[#F25C05] text-white rounded-3xl py-3 font-bold text-[16px] mb-4" />
                    
                </FlexboxLayout>
            </ScrollView>

            <BottomNav row="1" col="0" :activeTab="activeTab" @update:activeTab="activeTab = $event" class="mb-2"/>

        </GridLayout>
    </Page>
</template>

<style scoped>
TextField, TextView {
    font-weight: 500;
    border-width: 0;
    background: transparent;
    placeholder-color: #898989;
}

Button {
    android-elevation: 0;
}

Page {
    android-elevation: 0;
}

.switch-primary {
    android-checked-thumb-color: #F25C05;
    android-checked-track-color: #F25C0540;
}
</style>