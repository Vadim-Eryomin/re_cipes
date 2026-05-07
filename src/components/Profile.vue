<script lang="ts" setup>
import { 
    GridLayout, 
    Image, 
    Label, 
    ScrollView, 
    StackLayout, 
    FlexboxLayout,
    TextField,
    TextView,
    Button as NSButton
} from '@nativescript/core';
import { Dialogs } from '@nativescript/core';
import { ref, onMounted } from "nativescript-vue"
import { $navigateTo, $navigateBack } from 'nativescript-vue'
import MainPage from './MainPage.vue';
import Recipe from './Recipe.vue';
import RecipeMake from './RecipeMake.vue';
import Login from './Login.vue';
import Register from './Registration.vue';
import BottomNav from './BottomNav.vue';

const profile = ref({
    id: 'user_123',
    name: '@mili_Vasya',
    avatarUrl: '~/assets/test1.png',
    created_at: '2024-01-15T10:30:00Z'
})

const userPosts = ref([
    {
        id: 'post_2',
        author: { name: '@mili_Vasya', avatar_url: '~/assets/test1.png' },
        title: 'Паста Карбонара 🍝',
        description: 'Классический итальянский рецепт с кремовым соусом без сливок. Получилось очень вкусно!',
        text: 'Паста карбонара по-домашнему 🍝 Готовила впервые, но получилось отлично!',
        medias: ['~/assets/post2.png', '~/assets/post3.png'],
        created_at: new Date(Date.now() - 86400000).toISOString(),
        likes_count: 3,
        comments_count: 12
    },
    {
        id: 'post_3',
        author: { name: '@mili_Vasya', avatar_url: '~/assets/test1.png' },
        title: 'Шоколадный брауни 🍫',
        description: 'Невероятно влажный и шоколадный десерт. Секретный ингредиент - добавьте щепотку соли для контраста вкуса!',
        text: 'Шоколадный брауни — просто, быстро и безумно вкусно. Делюсь секретным ингредиентом 👇',
        medias: [],
        created_at: new Date(Date.now() - 172800000).toISOString(),
        likes_count: 0,
        comments_count: 0
    }
])

const activeTab = ref('profile')
const postVotes = ref<Record<string, number>>({})
const userVote = ref<Record<string, 'up' | 'down' | null>>({})

const isEditingName = ref(false)
const editedName = ref('')

const isEditingPost = ref(false)
const editingPostId = ref('')
const editedPostTitle = ref('')
const editedPostDescription = ref('')

onMounted(() => {
    userPosts.value.forEach(post => {
        postVotes.value[post.id] = post.likes_count
        userVote.value[post.id] = null
    })
})

function toFullUrl(path: string | null | undefined): string {
    if (!path) return ''
    if (path.startsWith('http://') || path.startsWith('https://')) return path
    return path
}

function formatDate(dateInput: string | Date | undefined): string {
    if (!dateInput) return '—'
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput
    if (isNaN(date.getTime())) return '—'
    const day = date.getDate().toString().padStart(2, '0')
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const year = date.getFullYear()
    return `${day}.${month}.${year}`
}

function formatDatePost(createdAt: string | Date | undefined): string {
    if (!createdAt) return 'недавно'
    const date = typeof createdAt === 'string' ? new Date(createdAt) : createdAt
    if (isNaN(date.getTime())) return 'недавно'
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    if (diffDays === 0) {
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        if (diffHours === 0) {
            const diffMinutes = Math.floor(diffMs / (1000 * 60))
            return diffMinutes < 1 ? 'только что' : `${diffMinutes} мин назад`
        }
        return `${diffHours} ч назад`
    }
    if (diffDays === 1) return '1 дн. назад'
    return `${diffDays} дн. назад`
}

function formatVotes(value: number): string {
    if (value > 0) return `+${value}`
    if (value < 0) return `${value}`
    return '0'
}

function voteColor(value: number): string {
    if (value > 0) return 'green-text'
    if (value < 0) return 'red-text'
    return 'white-text'
}

function voteUp(postId: string) {
    const currentVote = userVote.value[postId]
    const delta = currentVote === 'up' ? -1 : (currentVote === 'down' ? 2 : 1)
    if (currentVote === 'up') {
        userVote.value[postId] = null
    } else if (currentVote === 'down') {
        userVote.value[postId] = 'up'
    } else {
        userVote.value[postId] = 'up'
    }
    postVotes.value[postId] += delta
}

function voteDown(postId: string) {
    const currentVote = userVote.value[postId]
    const delta = currentVote === 'down' ? 1 : (currentVote === 'up' ? -2 : -1)
    if (currentVote === 'down') {
        userVote.value[postId] = null
    } else if (currentVote === 'up') {
        userVote.value[postId] = 'down'
    } else {
        userVote.value[postId] = 'down'
    }
    postVotes.value[postId] += delta
}

function startEditName() {
    editedName.value = profile.value.name
    isEditingName.value = true
}

function cancelEditName() {
    isEditingName.value = false
    editedName.value = ''
}

function saveEditName() {
    if (editedName.value.trim()) {
        profile.value.name = editedName.value.trim()
    }
    isEditingName.value = false
    editedName.value = ''
}

async function logout() {
    const confirm = await Dialogs.confirm({
        title: 'Выход из аккаунта',
        message: 'Вы действительно хотите выйти из аккаунта?',
        okButtonText: 'Да',
        cancelButtonText: 'Нет'
    })
    if (confirm) {
        $navigateTo(Login, { transition: { name: "slideLeft" }, clearHistory: true })
    }
}

async function deleteAccount() {
    const confirm = await Dialogs.confirm({
        title: 'Удаление аккаунта',
        message: 'Вы действительно хотите удалить аккаунт? Это действие нельзя отменить.',
        okButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
    })
    if (confirm) {
        $navigateTo(Register, { transition: { name: "slideLeft" }, clearHistory: true })
    }
}

async function deletePost(postId: string) {
    const confirm = await Dialogs.confirm({
        title: 'Удаление поста',
        message: 'Вы действительно хотите удалить этот пост?',
        okButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
    })
    if (confirm) {
        const idx = userPosts.value.findIndex(p => p.id === postId)
        if (idx !== -1) {
            userPosts.value.splice(idx, 1)
            delete postVotes.value[postId]
            delete userVote.value[postId]
        }
    }
}

function editPost(postId: string) {
    const post = userPosts.value.find(p => p.id === postId)
    if (post) {
        editingPostId.value = post.id
        editedPostTitle.value = post.title || ''
        editedPostDescription.value = post.description || ''
        isEditingPost.value = true
    }
}

function cancelEditPost() {
    isEditingPost.value = false
    editingPostId.value = ''
    editedPostTitle.value = ''
    editedPostDescription.value = ''
}

function saveEditPost() {
    if (!editedPostTitle.value.trim()) return
    const post = userPosts.value.find(p => p.id === editingPostId.value)
    if (post) {
        post.title = editedPostTitle.value.trim()
        post.description = editedPostDescription.value.trim()
        post.text = editedPostTitle.value.trim()
    }
    isEditingPost.value = false
    editingPostId.value = ''
    editedPostTitle.value = ''
    editedPostDescription.value = ''
}

function goToMain() {
    $navigateTo(MainPage, { transition: { name: "slideLeft" } })
}

function goToCreation() {
    $navigateTo(RecipeMake, { transition: { name: "slideLeft" } })
}

function goToRecipe(postId: string) {
    $navigateTo(Recipe, {
        props: { postId },
        transition: { name: "slideLeft" }
    })
}

function preventClose(event: any) {
    event.cancelBubble = true
}
</script>

<template>
    <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
        <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
            
            <ScrollView row="0" col="0">
                <FlexboxLayout flexDirection="column" alignItems="stretch" class="px-4 pt-8 pb-24">
                    
                    <FlexboxLayout flexDirection="row" alignItems="center" class="mb-4 pb-4 border-b border-[#393939]">
                        <Image :src="toFullUrl(profile?.avatarUrl)" 
                            class="w-20 h-20 rounded-full mr-4" />
                        <StackLayout verticalAlignment="center" class="flex-1">
                            <FlexboxLayout flexDirection="row" alignItems="center">
                                <Label :text="profile?.name" class="text-white font-bold text-[16px]" />
                                <Image src="~/assets/Edit_fill.png" width="20" height="20" class="ml-2" 
                                    @tap="startEditName" />
                            </FlexboxLayout>
                            <Label :text="'Аккаунт создан: ' + formatDate(profile?.created_at)" 
                                class="text-[#C7C7C7] text-[12px] mt-1" />
                        </StackLayout>
                    </FlexboxLayout>

                    <FlexboxLayout flexDirection="row" class="mb-6">
                        <NSButton @tap="logout" textTransform="none"
                            class="bg-[#393939] text-white rounded-xl px-4 py-2 text-[14px] mr-2">
                            Выйти из аккаунта
                        </NSButton>
                        <NSButton @tap="deleteAccount" textTransform="none"
                            class="bg-[#FF4444] text-white rounded-xl px-4 py-2 text-[14px]">
                            Удалить аккаунт
                        </NSButton>
                    </FlexboxLayout>

                    <StackLayout v-if="userPosts.length === 0" class="py-10">
                        <Label text="У вас пока нет постов" 
                            class="text-[#C7C7C7] text-[14px] text-center" />
                    </StackLayout>

                    <StackLayout v-for="(post, index) in userPosts" :key="post.id">
                        <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4">
                            
                            <FlexboxLayout flexDirection="row" justifyContent="flex-end" class="mb-2">
                                <Image src="~/assets/Edit_fill.png" width="24" height="24" class="mr-3" 
                                    @tap="() => editPost(post.id)" />
                                <Image src="~/assets/Trash.png" width="24" height="24" 
                                    @tap="() => deletePost(post.id)" />
                            </FlexboxLayout>

                            <FlexboxLayout flexDirection="row" alignItems="center" class="mb-3">
                                <Image :src="toFullUrl(post.author.avatar_url)" 
                                    class="w-10 h-10 rounded-full mr-3" />
                                <StackLayout verticalAlignment="center" class="flex-1">
                                    <Label :text="post.author.name" 
                                        class="text-white font-bold text-[14px]" />
                                </StackLayout>
                                <Label :text="formatDatePost(post.created_at)" 
                                    class="text-[#C7C7C7] text-[12px]" />
                            </FlexboxLayout>

                            <Label :text="post.title || 'Без названия'" 
                                class="text-white font-bold text-[16px] mb-2" textWrap="true" />
                            
                            <Label v-if="post.description" :text="post.description" 
                                class="text-[#C7C7C7] text-[13px] mb-3" textWrap="true" />

                            <Label :text="post.text" 
                                class="text-white text-[14px] mb-3" textWrap="true" />

                            <StackLayout v-for="(media, idx) in post.medias" :key="idx" class="mb-3">
                                <Image :src="toFullUrl(media)" 
                                    class="w-full rounded-xl" stretch="aspectFill" 
                                    @tap="() => goToRecipe(post.id)" />
                            </StackLayout>

                            <FlexboxLayout flexDirection="row" alignItems="center" class="mt-2">
                                <FlexboxLayout class="bg-[#121212] rounded-4xl border border-[#393939]" 
                                    flexDirection="row" alignItems="center" height="30">
                                    <Image :src="userVote[post.id] === 'up' ? '~/assets/arrow_up.png' : '~/assets/arrow_up (1).png'" 
                                        class="ml-3" width="24" height="24" @tap="() => voteUp(post.id)" />
                                    <Label :text="formatVotes(postVotes[post.id] || 0)"
                                        :class="['mx-2 text-center', voteColor(postVotes[post.id] || 0)]" width="28" />
                                    <Image :src="userVote[post.id] === 'down' ? '~/assets/arrow_down.png' : '~/assets/arrow_down (1).png'" 
                                        class="mr-3" width="24" height="24" @tap="() => voteDown(post.id)" />
                                </FlexboxLayout>

                                <FlexboxLayout class="bg-[#121212] rounded-4xl border border-[#393939] ml-3" 
                                    flexDirection="row" alignItems="center" height="30"
                                    @tap="() => goToRecipe(post.id)">
                                    <Image src="~/assets/Chat_alt.png" class="ml-3" width="18" height="18" />
                                    <Label :text="post.comments_count.toString()" 
                                        class="text-white ml-2 mr-3 text-[12px]" />
                                </FlexboxLayout>
                            </FlexboxLayout>
                            
                        </StackLayout>

                        <GridLayout v-if="index < userPosts.length - 1" height="1" class="my-4" backgroundColor="#393939" />
                        
                    </StackLayout>
                    
                </FlexboxLayout>
            </ScrollView>

            <BottomNav row="1" col="0" :activeTab="activeTab" @update:activeTab="activeTab = $event" class="mb-2"/>

            <GridLayout v-if="isEditingName" 
                rows="*" columns="*"
                backgroundColor="rgba(0,0,0,0.7)"
                verticalAlignment="center" horizontalAlignment="center"
                @tap="cancelEditName" zIndex="1000">
                <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mx-8" 
                    width="80%" @tap="preventClose">
                    <Label text="Редактировать имя" class="text-white font-bold text-[16px] mb-3 text-center" />
                    <TextField v-model="editedName" 
                        class="bg-[#121212] text-white rounded-xl px-3 py-2 mb-4 text-[14px]" 
                        hint="Введите новое имя" />
                    <FlexboxLayout flexDirection="row" justifyContent="space-between">
                        <NSButton @tap="cancelEditName" textTransform="none" 
                            class="bg-[#393939] text-white rounded-xl px-4 py-2 text-[14px] flex-1 mr-2">
                            Отмена
                        </NSButton>
                        <NSButton @tap="saveEditName" textTransform="none" 
                            class="bg-[#F25C05] text-white rounded-xl px-4 py-2 text-[14px] flex-1 ml-2">
                            Сохранить
                        </NSButton>
                    </FlexboxLayout>
                </StackLayout>
            </GridLayout>

            <GridLayout v-if="isEditingPost" 
                rows="*" columns="*"
                backgroundColor="rgba(0,0,0,0.7)"
                verticalAlignment="center" horizontalAlignment="center"
                @tap="cancelEditPost" zIndex="1000">
                <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mx-8" 
                    width="80%" @tap="preventClose">
                    <Label text="Редактировать пост" class="text-white font-bold text-[16px] mb-3 text-center" />
                    <Label text="Название поста *" class="text-[#C7C7C7] text-[12px] mb-1" />
                    <TextField v-model="editedPostTitle" 
                        class="bg-[#121212] text-white rounded-xl px-3 py-2 mb-3 text-[14px]" 
                        hint="Введите название..." />
                    <Label text="Описание" class="text-[#C7C7C7] text-[12px] mb-1" />
                    <TextView v-model="editedPostDescription" 
                        class="bg-[#121212] text-white rounded-xl p-3 mb-4 text-[14px]" 
                        hint="Добавьте описание..." height="80" />
                    <FlexboxLayout flexDirection="row" justifyContent="space-between">
                        <NSButton @tap="cancelEditPost" textTransform="none" 
                            class="bg-[#393939] text-white rounded-xl px-4 py-2 text-[14px] flex-1 mr-2">
                            Отмена
                        </NSButton>
                        <NSButton @tap="saveEditPost" textTransform="none" 
                            class="bg-[#F25C05] text-white rounded-xl px-4 py-2 text-[14px] flex-1 ml-2">
                            Сохранить
                        </NSButton>
                    </FlexboxLayout>
                </StackLayout>
            </GridLayout>

        </GridLayout>
    </Page>
</template>

<style scoped>
.green-text {
    color: #479A0F;
}

.red-text {
    color: #FF4444;
}

.white-text {
    color: #FFFFFF;
}

.text-center {
    text-align: center;
}

Page {
    android-elevation: 0;
}

Button {
    android-elevation: 0;
}

TextField, TextView {
    font-weight: 500;
    border-width: 0;
    background: transparent;
    placeholder-color: #898989;
}
</style>