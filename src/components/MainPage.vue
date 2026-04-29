<script lang="ts" setup>
import { AbsoluteLayout, ActivityIndicator, GridLayout, Image, Label, ScrollView, StackLayout, TextField } from '@nativescript/core';
import { ref, onMounted, computed, watch } from "nativescript-vue"
import { Screen } from '@nativescript/core/platform';
import { $navigateTo } from 'nativescript-vue'
import Profile from './Profile.vue';
import Recipe from './Recipe.vue';
import { createLoadingMachine } from '~/reusable/loadingMachine'
import { useMachine } from '@xstate/vue'
import { postsService } from '~/init/services'
import { ajaxService } from '~/init/ajax'
import type { Post } from '~/features/domain/posts/models/post'
import RecipeMake from './RecipeMake.vue';

const sortOptions = ["Лучшие", "Новые", "Блины", "Борщ", "Салаты", "Горячее"]
const selectedSort = ref("Новые")
const dropdownOpen = ref(false)

const sortButton = ref<any>()
const dropdownTop = ref(0)
const dropdownLeft = ref(0)

const navTop = ref(0)
const navLeft = ref(0)

const feedMachine = createLoadingMachine(
  { limit: 20, offset: 0 },
  (query) => postsService.getFeed(query.limit, query.offset)
)
const { snapshot: feedState, send: sendFeed } = useMachine(feedMachine)

const posts = computed(() => (feedState.value.context.data as Post[]) || [])
const isLoading = computed(() => feedState.value.matches('loading'))

const postVotes = ref<Record<string, number>>({})
const userVote = ref<Record<string, 'up' | 'down' | null>>({})

function toFullUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const baseUrl = (ajaxService as any)._baseURL
  return baseUrl + (path.startsWith('/') ? path : '/' + path)
}

function formatDate(createdAt: string | Date | undefined): string {
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
  return ''
}

async function voteUp(postId: string) {
  const current = userVote.value[postId]
  const delta = current === 'up' ? -1 : (current === 'down' ? 2 : 1)

  if (current === 'up') userVote.value[postId] = null
  else if (current === 'down') userVote.value[postId] = 'up'
  else userVote.value[postId] = 'up'

  postVotes.value[postId] = (postVotes.value[postId] || 0) + delta

  try {
    if (current === 'up') await postsService.unlikePost(postId)
    else await postsService.likePost(postId)
  } catch (e) {
    userVote.value[postId] = current
    postVotes.value[postId] = (postVotes.value[postId] || 0) - delta
    console.error(e)
  }
}

async function voteDown(postId: string) {
  const current = userVote.value[postId]
  const delta = current === 'down' ? 1 : (current === 'up' ? -2 : -1)

  if (current === 'down') userVote.value[postId] = null
  else if (current === 'up') userVote.value[postId] = 'down'
  else userVote.value[postId] = 'down'

  postVotes.value[postId] = (postVotes.value[postId] || 0) + delta

  try {
    if (current === 'down') await postsService.likePost(postId)
    else await postsService.unlikePost(postId)
  } catch (e) {
    userVote.value[postId] = current
    postVotes.value[postId] = (postVotes.value[postId] || 0) - delta
    console.error(e)
  }
}

function toggleDropdown() {
  const btn = sortButton.value?.nativeView
  if (btn) {
    const location = btn.getLocationRelativeTo(btn.page)
    dropdownTop.value = location.y
    dropdownLeft.value = location.x
  }
  dropdownOpen.value = !dropdownOpen.value
}

function closeDropdown() {
  dropdownOpen.value = false
}

function selectSort(option: string) {
  selectedSort.value = option
  dropdownOpen.value = false
}

function goToProfile() {
  $navigateTo(Profile, { transition: { name: "slideLeft" } })
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

watch(posts, (newPosts: Post[]) => {
  newPosts.forEach((post: Post) => {
    if (!(post.id in postVotes.value)) {
      postVotes.value[post.id] = post.likes_count || 0
      userVote.value[post.id] = null
    }
  })
})

onMounted(() => {
  const screenWidth = Screen.mainScreen.widthDIPs
  const screenHeight = Screen.mainScreen.heightDIPs
  const navWidth = 250
  const navHeight = 60

  navTop.value = screenHeight - navHeight - 100
  navLeft.value = (screenWidth - navWidth) / 2

  sendFeed({ type: 'LOAD' })
})
</script>

<template>
  <Page actionBarHidden="true">
    <AbsoluteLayout>
      <ScrollView width="100%" height="100%">
        <StackLayout>

          <!-- Лого + Поиск -->
          <StackLayout orientation="horizontal" verticalAlignment="center" class="mt-2">
            <Image class="m-4" width="50" src="~/assets/logo.png" />
            <GridLayout class="bg-gray-200 rounded-4xl mr-4" columns="auto,*" height="50" verticalAlignment="center">
              <Image col="0" src="~/assets/search-icon.png" class="m-4" width="20" height="20" />
              <TextField col="1" hint="Поиск в reCipes" class="search-input" editable="true" />
            </GridLayout>
          </StackLayout>

          <!-- Сортировка -->
          <StackLayout class="sort-container w-full">
            <StackLayout ref="sortButton" class="dropdown-container p-3 pl-4" orientation="horizontal"
              @tap="toggleDropdown">
              <Label :text="selectedSort" class="font-bold" />
              <Label text=" ▼" class="ml-1" />
            </StackLayout>
          </StackLayout>

          <!-- Индикатор загрузки -->
          <ActivityIndicator v-if="isLoading" busy="true" class="m-10" />

          <!-- Список постов -->
          <StackLayout v-else v-for="post in posts" :key="post.id" class="mb-8">

            <!-- Шапка поста -->
            <StackLayout orientation="horizontal" verticalAlignment="center" class="mx-4 mt-3">
              <Image class="mr-3 rounded-full" width="65" :src="toFullUrl(post.author.avatar_url)" />
              <StackLayout verticalAlignment="center">
                <Label :text="'r/' + post.community" class="text-sm font-bold" />
                <Label :text="'@' + post.author.name" class="text-sm font-bold" />
              </StackLayout>
              <Label :text="formatDate(post.created_at)" class="text-sm text-gray-500 ml-3" />
            </StackLayout>

            <!-- Текст -->
            <Label :text="post.text" class="text-sm mx-4 mt-2" textWrap="true" />

            <!-- Изображение -->
            <Image v-if="post.medias && post.medias.length" class="m-4 rounded-3xl" :src="toFullUrl(post.medias[0])" />

            <!-- Кнопки действий -->
            <StackLayout orientation="horizontal" verticalAlignment="center" class="mx-4 mt-2">
              <StackLayout class="bg-gray-200 rounded-4xl" orientation="horizontal" height="50"
                verticalAlignment="center">
                <Image src="~/assets/arrow_up.png" class="ml-3" width="30" height="30" @tap="() => voteUp(post.id)"
                  :opacity="userVote[post.id] === 'up' ? 0.7 : 1" />
                <Label :text="formatVotes(postVotes[post.id] || 0)"
                  :class="['mx-2 text-center', voteColor(postVotes[post.id] || 0)]" width="32" />
                <Image src="~/assets/arrow_down.png" class="mr-3" width="30" height="30" @tap="() => voteDown(post.id)"
                  :opacity="userVote[post.id] === 'down' ? 0.7 : 1" />
              </StackLayout>

              <StackLayout class="bg-gray-200 rounded-4xl ml-3" orientation="horizontal" height="50"
                verticalAlignment="center" @tap="() => goToRecipe(post.id)">
                <Image src="~/assets/commentary.png" class="ml-3" width="30" height="30" />
                <Label :text="'0'" class="search-input ml-2 mr-3" />
              </StackLayout>
            </StackLayout>
          </StackLayout>

        </StackLayout>
      </ScrollView>

      <!-- Оверлей для закрытия дропдауна -->
      <GridLayout v-if="dropdownOpen" width="100%" height="100%" @tap="closeDropdown" />

      <!-- Дропдаун сортировки -->
      <StackLayout v-if="dropdownOpen" class="dropdown-menu" :left="dropdownLeft" :top="dropdownTop">
        <Label text="Сортировка по:" class="dropdown-title" />
        <Label v-for="option in sortOptions" :key="option" :text="option" class="p-3 px-4"
          :class="{ selected: option === selectedSort }" @tap="selectSort(option)" />
      </StackLayout>

      <!-- Нижняя навигация -->
      <StackLayout orientation="horizontal" height="60" width="250" :top="navTop" :left="navLeft"
        class="bg-gray rounded-full mb-4" verticalAlignment="center" horizontalAlignment="center" @loaded="onNavLoaded">
        <Image src="~/assets/home-active.png" width="30" height="30" />
        <StackLayout width="60" height="60" class="plus-button bg-orange rounded-full mx-7" verticalAlignment="center"
          horizontalAlignment="center">
          <Image src="~/assets/plus.png" width="30" height="30" @tap="goToCreation" />
        </StackLayout>
        <Image src="~/assets/profile-inactive.png" width="30" height="30" @tap="goToProfile" />
      </StackLayout>
    </AbsoluteLayout>
  </Page>
</template>

<style>
.search-input {
  font-weight: 500;
  border-width: 0;
  border-bottom-width: 0;
  border-bottom-color: transparent;
  background: transparent;
}

.sort-container {
  border-top-width: 2;
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