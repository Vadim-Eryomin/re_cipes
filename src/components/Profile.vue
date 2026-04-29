<script lang="ts" setup>
import { AbsoluteLayout, Button, FormattedString, GridLayout, Image, Label, ScrollView, StackLayout, TextField, ActivityIndicator } from '@nativescript/core';
import { ref, onMounted, computed, watch } from "nativescript-vue"
import { Screen } from '@nativescript/core/platform';
import { $navigateTo } from 'nativescript-vue'
import MainPage from './MainPage.vue';
import Recipe from './Recipe.vue';
import { createLoadingMachine } from '~/reusable/loadingMachine'
import { useMachine } from '@xstate/vue'
import { usersService, postsService } from '~/init/services'
import { ajaxService } from '~/init/ajax'
import type { UserRecord } from '~/features/domain/users/models/user'
import type { Post } from '~/features/domain/posts/models/post'
import RecipeMake from './RecipeMake.vue';

const navTop = ref(0)
const navLeft = ref(0)

function toFullUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const baseUrl = (ajaxService as any)._baseURL
  return baseUrl + path
}

const profileMachine = createLoadingMachine(
  {},
  () => usersService.getMyProfile()
)
const { snapshot: profileState, send: sendProfile } = useMachine(profileMachine)

const myPostsMachine = createLoadingMachine(
  { limit: 20, offset: 0 },
  (query) => postsService.getMyPosts(query.limit, query.offset)
)
const { snapshot: postsState, send: sendPosts } = useMachine(myPostsMachine)

const profile = computed(() => profileState.value.context.data as UserRecord | undefined)
const userPosts = computed(() => (postsState.value.context.data as Post[]) || [])

const isLoadingProfile = computed(() => profileState.value.matches('loading'))
const isLoadingPosts = computed(() => postsState.value.matches('loading'))

const postVotes = ref<Record<string, number>>({})
const userVote = ref<Record<string, 'up' | 'down' | null>>({})

watch(userPosts, (posts) => {
  posts.forEach(post => {
    if (!(post.id in postVotes.value)) {
      postVotes.value[post.id] = post.likes_count
      userVote.value[post.id] = null
    }
  })
})

async function voteUp(postId: string) {
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

  try {
    if (currentVote === 'up') {
      await postsService.unlikePost(postId)
    } else if (currentVote === 'down') {
      await postsService.likePost(postId)
    } else {
      await postsService.likePost(postId)
    }
  } catch (error) {
    if (currentVote === 'up') {
      userVote.value[postId] = 'up'
      postVotes.value[postId] -= delta
    } else if (currentVote === 'down') {
      userVote.value[postId] = 'down'
      postVotes.value[postId] -= delta
    } else {
      userVote.value[postId] = null
      postVotes.value[postId] -= delta
    }
    console.error('Failed to vote up:', error)
  }
}

async function voteDown(postId: string) {
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

  try {
    if (currentVote === 'down') {
      await postsService.likePost(postId)
    } else if (currentVote === 'up') {
      await postsService.unlikePost(postId)
    } else {
      await postsService.unlikePost(postId)
    }
  } catch (error) {
    if (currentVote === 'down') {
      userVote.value[postId] = 'down'
      postVotes.value[postId] -= delta
    } else if (currentVote === 'up') {
      userVote.value[postId] = 'up'
      postVotes.value[postId] -= delta
    } else {
      userVote.value[postId] = null
      postVotes.value[postId] -= delta
    }
    console.error('Failed to vote down:', error)
  }
}

function formatVotes(value: number): string {
  if (value > 0) return `+${value}`
  if (value < 0) return `${value}`
  return '0'
}

function voteColor(value: number): string {
  if (value > 0) return 'green-text'
  if (value < 0) return 'red-text'
  return ''
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

function onNavLoaded(args: any) {
  const view = args.object.nativeView
  if (view?.getParent) {
    const parent = view.getParent()
    if (parent?.setClipChildren) {
      parent.setClipChildren(false)
    }
  }
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

onMounted(() => {
  const screenWidth = Screen.mainScreen.widthDIPs
  const screenHeight = Screen.mainScreen.heightDIPs
  const navWidth = 250
  const navHeight = 60

  navTop.value = screenHeight - navHeight - 100
  navLeft.value = (screenWidth - navWidth) / 2

  sendProfile({ type: 'LOAD' })
  sendPosts({ type: 'LOAD' })
})
</script>

<template>
  <Page actionBarHidden="true">
    <AbsoluteLayout>
      <ScrollView width="100%" height="100%">
        <StackLayout>
          <!-- Профиль -->
          <ActivityIndicator v-if="isLoadingProfile" busy="true" class="m-10" />
          <StackLayout v-else-if="profile" class="profile-header" orientation="horizontal" verticalAlignment="center">
            <Image class="mx-4 mt-3 mb-2" width="90" borderRadius="45" :src="toFullUrl(profile.avatarUrl)" />
            <StackLayout class="mr-4" verticalAlignment="center">
              <Label :text="profile.name" class="text-sm font-bold" />
              <Label :text="'Аккаунт создан: ' + formatDate(profile?.created_at)" class="text-sm text-gray-500" />
            </StackLayout>
          </StackLayout>

          <!-- Посты пользователя -->
          <ActivityIndicator v-if="isLoadingPosts" busy="true" class="m-10" />
          <StackLayout v-else-if="userPosts.length === 0" class="p-10 text-center">
            <Label text="У вас пока нет постов" class="text-gray-500 text-center" />
          </StackLayout>

          <StackLayout v-for="post in userPosts" :key="post.id" class="mb-6">
            <!-- Шапка поста -->
            <StackLayout orientation="horizontal" verticalAlignment="center">
              <Image class="mx-4 mt-3 mb-2 rounded-full" width="65" :src="toFullUrl(post.author.avatar_url)" />
              <StackLayout class="mr-4" verticalAlignment="center">
                <Label :text="post.author.name" class="text-sm font-bold" />
              </StackLayout>
              <Label :text="formatDatePost(post.created_at)" class="text-sm text-gray-500 ml-3" />
            </StackLayout>

            <!-- Текст поста -->
            <Label :text="post.text" class="text-sm mx-4" textWrap="true" />

            <!-- Медиа -->
            <Image v-for="(media, idx) in post.medias" :key="idx" class="m-4 rounded-3xl" :src="toFullUrl(media)" />

            <!-- Кнопки лайков и комментариев -->
            <StackLayout orientation="horizontal" verticalAlignment="center">
              <StackLayout class="bg-gray-200 rounded-4xl mx-4" orientation="horizontal" height="50"
                verticalAlignment="center" width="auto">
                <Image src="~/assets/arrow_up.png" class="ml-3" width="30" height="30" @tap="() => voteUp(post.id)"
                  :opacity="userVote[post.id] === 'up' ? 0.7 : 1" />
                <Label :text="formatVotes(postVotes[post.id] || 0)"
                  :class="['text-center mx-2', voteColor(postVotes[post.id] || 0)]" width="30" />
                <Image src="~/assets/arrow_down.png" class="mr-3" width="30" height="30" @tap="() => voteDown(post.id)"
                  :opacity="userVote[post.id] === 'down' ? 0.7 : 1" />
              </StackLayout>

              <StackLayout class="bg-gray-200 rounded-4xl" orientation="horizontal" height="50"
                verticalAlignment="center" width="auto" @tap="() => goToRecipe(post.id)">
                <Image src="~/assets/commentary.png" class="ml-3" width="30" height="30" />
                <Label text="0" class="search-input ml-2 mr-3" />
              </StackLayout>
            </StackLayout>
          </StackLayout>
        </StackLayout>
      </ScrollView>

      <!-- Нижняя навигация -->
      <StackLayout orientation="horizontal" height="60" width="250" :top="navTop" :left="navLeft"
        class="bg-gray rounded-full mb-4" verticalAlignment="center" horizontalAlignment="center" @loaded="onNavLoaded">
        <Image src="~/assets/home-inactive.png" width="30" height="30" @tap="goToMain" />
        <StackLayout width="60" height="60" class="plus-button bg-orange rounded-full mx-7" verticalAlignment="center"
          horizontalAlignment="center">
          <Image src="~/assets/plus.png" width="30" height="30" @tap="goToCreation" />
        </StackLayout>
        <Image src="~/assets/profile-active.png" width="30" height="30" />
      </StackLayout>
    </AbsoluteLayout>
  </Page>
</template>

<style scoped>
.search-input {
  font-weight: 500;
  border-width: 0;
  border-bottom-width: 0;
  border-bottom-color: transparent;
  background: transparent;
}

.profile-header {
  border-bottom-width: 2;
  border-color: #949090;
}

.dropdown-container {
  font-weight: 600;
  font-size: 16;
  color: #636363
}

.dropdown-menu {
  width: 180;
  background-color: white;
  border-radius: 12;
  border-color: #949090;
  padding: 8;
}

.dropdown-title {
  font-size: 12;
  color: #888;
  margin-bottom: 6;
}

.selected {
  background-color: #eeeeee;
}

.green-text {
  color: #479A0F;
}

.red-text {
  color: #FF4444;
}

.text-center {
  text-align: center;
}

.plus-button {
  margin-top: -50;
  justify-content: center;
  align-items: center;
}

.bg-gray {
  background-color: #E9E9ED;
}

.bg-orange {
  background-color: #FF6600;
}

.rounded-full {
  border-radius: 30;
}
</style>