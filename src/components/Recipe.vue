<script lang="ts" setup>
import { Image, Label, ScrollView, StackLayout, TextField, GridLayout, ActivityIndicator } from '@nativescript/core';
import { ref, onMounted } from "nativescript-vue"
import { postsService, usersService } from '~/init/services'
import { ajaxService } from '~/init/ajax'
import type { Post } from '~/features/domain/posts/models/post'

const props = defineProps<{ postId: string }>()

const post = ref<Post | null>(null)
const commentsTree = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const newCommentText = ref('')
const currentUserAvatar = ref('')

const postVotes = ref(0)
const userVote = ref<null | 'up' | 'down'>(null)

function toFullUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const baseUrl = (ajaxService as any)._baseURL
  return baseUrl + path
}

function buildCommentsTree(flatComments: any[]): any[] {
  const map = new Map()
  const roots: any[] = []
  flatComments.forEach(comment => {
    map.set(comment.id, { ...comment, replies: [] })
  })
  flatComments.forEach(comment => {
    const node = map.get(comment.id)
    if (comment.parent_id && map.has(comment.parent_id)) {
      map.get(comment.parent_id).replies.push(node)
    } else {
      roots.push(node)
    }
  })
  roots.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  roots.forEach(root => {
    root.replies.sort((a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
  })
  return roots
}

async function loadCurrentUser() {
  try {
    const user = await usersService.getMyProfile()
    currentUserAvatar.value = toFullUrl(user.avatarUrl)
  } catch (err) {
    currentUserAvatar.value = '~/assets/user_avatar.png'
  }
}

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [postData, commentsData] = await Promise.all([
      postsService.getPost(props.postId),
      postsService.getComments(props.postId)
    ])
    post.value = postData
    postVotes.value = postData.likes_count

    const flat = commentsData.map((c: any) => ({
      id: c.id,
      user: `@${c.author.name}`,
      avatar: toFullUrl(c.author.avatar_url),
      time: formatDate(c.created_at),
      text: c.text,
      parent_id: c.parent_id,
      created_at: c.created_at
    }))
    commentsTree.value = buildCommentsTree(flat)
  } catch (err: any) {
    error.value = err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

function formatDate(createdAt: string | Date): string {
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

async function voteUp() {
  if (userVote.value === 'up') {
    postVotes.value -= 1
    userVote.value = null
    await postsService.unlikePost(props.postId).catch(console.error)
  } else if (userVote.value === 'down') {
    postVotes.value += 2
    userVote.value = 'up'
    await postsService.likePost(props.postId).catch(console.error)
  } else {
    postVotes.value += 1
    userVote.value = 'up'
    await postsService.likePost(props.postId).catch(console.error)
  }
}

async function voteDown() {
  if (userVote.value === 'down') {
    postVotes.value += 1
    userVote.value = null
    await postsService.likePost(props.postId).catch(console.error)
  } else if (userVote.value === 'up') {
    postVotes.value -= 2
    userVote.value = 'down'
    await postsService.unlikePost(props.postId).catch(console.error)
  } else {
    postVotes.value -= 1
    userVote.value = 'down'
    await postsService.unlikePost(props.postId).catch(console.error)
  }
}

function formatVotes(value: number): string {
  if (value > 0) return `+${value}`
  if (value < 0) return `${value}`
  return '0'
}

function voteColor() {
  if (postVotes.value > 0) return 'green-text'
  if (postVotes.value < 0) return 'red-text'
  return ''
}

onMounted(() => {
  loadData()
  loadCurrentUser()
})
</script>

<template>
  <Page actionBarHidden="true">
    <AbsoluteLayout>
      <ScrollView width="100%" height="100%">
        <StackLayout>
          <ActivityIndicator v-if="loading" busy="true" class="m-10" />
          
          <StackLayout v-else-if="post">
            <!-- Шапка поста -->
            <StackLayout orientation="horizontal" verticalAlignment="center">
              <Image class="mx-4 mt-3 mb-2 rounded-full" width="65" :src="toFullUrl(post.author.avatar_url)" />
              <StackLayout class="mr-4" verticalAlignment="center">
                <Label :text="'r/' + post.community" class="text-sm font-bold"/>
                <Label :text="'@' + post.author.name" class="text-sm font-bold"/>
              </StackLayout>
              <Label :text="formatDate(post.created_at)" class="text-sm text-gray-500"/>
            </StackLayout>

            <!-- Текст поста -->
            <Label :text="post.text" class="text-sm mx-4"textWrap="true" />
            
            <!-- Изображение поста -->
            <Image v-if="post.medias && post.medias.length" class="m-4 rounded-3xl" :src="toFullUrl(post.medias[0])" />

            <!-- Ингредиенты -->
            <StackLayout class="bg-gray-200 rounded-3xl mx-4 p-4 mb-4">
              <Label text="Ингредиенты" class="text-center font-bold text-lg mb-3"/>
              <StackLayout v-for="ingredient in post.ingredients" :key="ingredient.name" class="mb-2">
                <GridLayout columns="auto,*,auto">
                  <Label col="0" :text="ingredient.name" />
                  <StackLayout col="1" height="1" class="bg-gray-400 mx-2" verticalAlignment="center"/>
                  <Label col="2" :text="ingredient.count + ' ' + ingredient.measure_name" />
                </GridLayout>
              </StackLayout>
            </StackLayout>

            <!-- Шаги рецепта -->
            <StackLayout>
              <StackLayout v-for="(step, idx) in post.recipe" :key="idx" class="bg-gray-200 rounded-3xl mx-4 mb-4">
                <GridLayout columns="120,*">
                  <GridLayout col="0" width="120" height="100">
                    <Image v-if="step.media" :src="toFullUrl(step.media)" width="120" height="120" stretch="aspectFill" class="rounded-2xl"/>
                    <Label :text="(idx+1).toString()" width="28" height="28" class="bg-orange-500 text-white text-center rounded-full m-2" horizontalAlignment="left" verticalAlignment="bottom"/>
                  </GridLayout>
                  <Label col="1" :text="step.step" textWrap="true" class="text-sm mx-3" verticalAlignment="center" />
                </GridLayout>
              </StackLayout>
            </StackLayout>

            <!-- Кнопки лайков/комментариев -->
            <StackLayout orientation="horizontal" verticalAlignment="center">
              <StackLayout class="bg-gray-200 rounded-4xl mx-4" orientation="horizontal" height="50" verticalAlignment="center" width="auto">
                <Image src="~/assets/arrow_up.png" class="ml-3" width="30" height="30" @tap="voteUp()"/>
                <Label :text="formatVotes(postVotes)" :class="['text-center mx-2', voteColor()]" width="30" />
                <Image src="~/assets/arrow_down.png" class="mr-3" width="30" height="30" @tap="voteDown()"/>
              </StackLayout>
              <StackLayout class="bg-gray-200 rounded-4xl" orientation="horizontal" height="50" verticalAlignment="center" width="auto">
                <Image src="~/assets/commentary.png" class="ml-3" width="30" height="30"/>
                <Label :text="commentsTree.length.toString()" class="search-input ml-2 mr-3"/>
              </StackLayout>
            </StackLayout>
          </StackLayout>

          <GridLayout height="1" class="mt-3" backgroundColor="#949090" width="100%"/>

          <!-- Комментарии -->
          <StackLayout class="mx-4 mt-4">
            <StackLayout orientation="horizontal" verticalAlignment="center">
              <Image :src="currentUserAvatar" width="45" height="45" class="rounded-full"/>
              <TextField v-model="newCommentText" hint="Напишите, что думаете..." class="bg-gray-200 rounded-3xl ml-3 px-4" height="45" width="100%"/>
            </StackLayout>

            <StackLayout v-for="comment in commentsTree" :key="comment.id" class="mt-4">
              <GridLayout columns="50,*" rows="auto,auto">
                <Image rowSpan="2" col="0" :src="comment.avatar" width="40" height="40" class="rounded-full" verticalAlignment="top"/>
                <StackLayout row="0" col="1" orientation="horizontal">
                  <Label :text="comment.user" class="font-bold"/>
                  <Label :text="' ' + comment.time" class="text-gray-500"/>
                </StackLayout>
                <Label row="1" col="1" :text="comment.text" textWrap="true" class="text-sm mt-1"/>
              </GridLayout>

              <StackLayout
                v-if="comment.replies && comment.replies.length"
                class="ml-6 pl-3"
                marginTop="20"
                borderLeftWidth="2"
                borderLeftColor="#D1D5DB"
              >
                <StackLayout v-for="reply in comment.replies" :key="reply.id" class="mb-3">
                  <GridLayout columns="40,*" rows="auto,auto">
                    <Image rowSpan="2" col="0" :src="reply.avatar" width="35" height="35" class="rounded-full" verticalAlignment="top"/>
                    <StackLayout row="0" col="1" orientation="horizontal">
                      <Label :text="reply.user" class="font-bold"/>
                      <Label :text="' ' + reply.time" class="text-gray-500"/>
                    </StackLayout>
                    <Label row="1" col="1" :text="reply.text" textWrap="true" class="text-sm mt-1"/>
                  </GridLayout>
                </StackLayout>
              </StackLayout>
            </StackLayout>
          </StackLayout>
        </StackLayout>
      </ScrollView>
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
.green-text { 
  color: #479A0F; 
}
.red-text { 
  color: #FF4444; 
}
.text-center { 
  text-align: center; 
}
.bg-gray { 
  background-color: #E9E9ED; 
}
.bg-orange { 
  background-color: #FF6600; 
}
</style>