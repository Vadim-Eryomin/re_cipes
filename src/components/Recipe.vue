<script lang="ts" setup>
import { Image, Label, ScrollView, StackLayout, TextField, FlexboxLayout, ActivityIndicator, ListView } from '@nativescript/core';
import { ref, onMounted } from "nativescript-vue"
import BottomNav from './BottomNav.vue';
import { $navigateTo } from 'nativescript-vue';
import MainPage from './MainPage.vue';
import api, { mediaUrl } from '../../services/api';
import {
  mapRecipeToDetail,
  mapCommentToUi,
  buildCommentsTree,
} from '../../services/recipeUi';

const props = defineProps<{ postId: string }>()

const post = ref<any>(null)
const loading = ref(true)
const newCommentText = ref('')
const commentsTree = ref<any[]>([])
const activeTab = ref('main')
const replyTexts = ref<{ [key: string]: string }>({})
const currentUserAvatar = ref('')

function goBack() {
  $navigateTo(MainPage, {
    transition: { name: "slideRight" }
  })
}

function toFullUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return path
}

function formatVotes(value: number): string {
  if (value > 0) return `+${value}`
  if (value < 0) return `${value}`
  return '0'
}

function voteColor(value: number): string {
  if (value > 0) return 'green-text'
  if (value < 0) return 'orange-text'
  return ''
}

async function voteUp() {
  if (!post.value) return
  try {
    const result = await api.voteRecipe(props.postId, 'up')
    post.value.likes = result.score
    post.value.userLiked = result.user_vote === 1
    post.value.userDisliked = result.user_vote === -1
  } catch (e) {
    console.error('Vote failed:', e)
  }
}

async function voteDown() {
  if (!post.value) return
  try {
    const result = await api.voteRecipe(props.postId, 'down')
    post.value.likes = result.score
    post.value.userLiked = result.user_vote === 1
    post.value.userDisliked = result.user_vote === -1
  } catch (e) {
    console.error('Vote failed:', e)
  }
}

async function reloadComments() {
  const commentsResp = await api.getComments(props.postId)
  const flat = (commentsResp.items || []).map(mapCommentToUi)
  commentsTree.value = buildCommentsTree(flat)
  if (post.value) {
    post.value.comments = commentsResp.total ?? flat.length
  }
}

async function addComment() {
  if (!newCommentText.value || !newCommentText.value.trim()) return
  try {
    await api.addComment(props.postId, newCommentText.value.trim())
    newCommentText.value = ''
    await reloadComments()
  } catch (e) {
    console.error('Add comment failed:', e)
  }
}

async function addReply(commentId: string) {
  const replyText = replyTexts.value[commentId]
  if (!replyText || !replyText.trim()) return
  try {
    await api.addComment(props.postId, replyText.trim(), parseInt(commentId, 10))
    replyTexts.value[commentId] = ''
    await reloadComments()
  } catch (e) {
    console.error('Add reply failed:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const [recipe, me] = await Promise.all([
      api.getRecipe(props.postId),
      api.getMe().catch(() => null),
    ])

    post.value = mapRecipeToDetail(recipe)

    if (me?.image) {
      currentUserAvatar.value = mediaUrl(me.image.url || me.image.path)
    }

    if (recipe.comments?.length) {
      const flat = recipe.comments.map(mapCommentToUi)
      commentsTree.value = buildCommentsTree(flat)
    } else {
      await reloadComments()
    }
  } catch (e) {
    console.error('Failed to load recipe:', e)
    post.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
    <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
      
      <ScrollView row="0" col="0">
        <FlexboxLayout flexDirection="column" alignItems="stretch" class="px-4 pt-4 pb-4">
          
          <ActivityIndicator v-if="loading" busy="true" class="m-10" />
          
          <StackLayout v-else-if="post">
            <Image width="30" height="30" src="~/assets/Arrow_left.png" @tap="goBack" class="mb-2 mt-4" horizontalAlignment="left" />
            
            <GridLayout columns="auto, *, auto" class="mx-0 mt-1" verticalAlignment="center">
              <Image col="0" width="40" height="40" :src="toFullUrl(post.userAvatar)" class="rounded-full" />
              
              <StackLayout col="1" class="ml-2" verticalAlignment="center">
                <Label :text="post.topic" class="text-white font-bold text-[12px]" />
                <Label :text="post.userName" class="text-white text-[12px]" />
              </StackLayout>
              
              <Label col="2" :text="post.date" class="text-[#C7C7C7] text-[12px] font-normal text-right" />
            </GridLayout>

            <Label :text="post.title" class="text-white text-[15px] mx-0 mt-3" textWrap="true" />
            
            <Image v-if="post.image" class="mx-0 mt-3 rounded-xl" :src="toFullUrl(post.image)" width="100%" />

            <StackLayout v-if="post.ingredients && post.ingredients.length > 0" class="bg-[#1E1E1E] rounded-2xl mt-4" style="height: auto;">
              <Label text="Ингредиенты" class="text-white text-center font-bold text-[16px] pt-4 pb-2" />
              <ListView 
                :items="post.ingredients" 
                :height="post.ingredients.length * 50"
                separatorColor="transparent">
                <template #default="{ item }">
                  <GridLayout columns="auto,*,auto" class="px-4 py-3">
                    <Label col="0" :text="item.name" class="text-[#C7C7C7] text-[14px]" style="margin-right: 2;" />
                    <Label col="1" text="............................................................................................................" class="text-[#393939] text-[12px] text-center" style="margin-left: 2; margin-right: 2;" />
                    <Label col="2" :text="item.quantity + ' ' + item.unit" class="text-[#C7C7C7] text-[14px]" textAlignment="right" style="margin-left: 2;" />
                  </GridLayout>
                </template>
              </ListView>
            </StackLayout>

            <StackLayout class="mt-4">
              <Label text="Шаги приготовления" class="text-white font-bold text-[16px] mb-2 ml-1"/>
              <ListView :items="post.steps" height="auto" separatorColor="transparent">
                <template #default="{ item, index }">
                  <StackLayout>
                    <GridLayout columns="auto, *" style="width: 100%;">
                      <GridLayout col="0" class="relative" style="margin-left: 0;">
                        <Image :src="toFullUrl(item.image)" class="rounded-l-2xl" width="120" height="120" stretch="aspectFill" style="margin-left: 0;" />
                      </GridLayout>
                      <StackLayout col="1" class="bg-[#1E1E1E] rounded-r-2xl p-3" style="height: 120; margin-left: 0;" verticalAlignment="center">
                        <Label :text="'Шаг ' + item.order" class="text-[#F25C05] font-bold text-[14px] mb-1" />
                        <Label :text="item.description" class="text-white text-[14px]" textWrap="true" />
                      </StackLayout>
                    </GridLayout>
                    <GridLayout v-if="index < post.steps.length - 1" height="4" backgroundColor="#121212" style="margin-top: 2; margin-bottom: 2;" />
                  </StackLayout>
                </template>
              </ListView>
            </StackLayout>

            <StackLayout orientation="horizontal" verticalAlignment="center" class="mt-4">
              <StackLayout class="bg-[#121212] rounded-4xl border border-[#393939]" orientation="horizontal" height="30" verticalAlignment="center">
                <Image :src="post.userLiked ? '~/assets/arrow_up.png' : '~/assets/arrow_up (1).png'" class="ml-3" width="30" height="30" @tap="voteUp" />
                <Label :text="formatVotes(post.likes)" :class="['mx-2 text-center', voteColor(post.likes)]" width="32" />
                <Image :src="post.userDisliked ? '~/assets/arrow_down.png' : '~/assets/arrow_down (1).png'" class="mr-3" width="30" height="30" @tap="voteDown" />
              </StackLayout>

              <StackLayout class="bg-[#121212] rounded-4xl ml-3 border border-[#393939]" orientation="horizontal" height="30" verticalAlignment="center">
                <Image src="~/assets/Chat_alt.png" class="ml-3" width="20" height="20" color="white" />
                <Label :text="post.comments.toString()" class="search-input ml-2 mr-3 text-white" />
              </StackLayout>
            </StackLayout>

            <GridLayout height="1" class="mt-4" backgroundColor="#393939" width="100%"/>

            <StackLayout class="mt-4">
              <Label text="Комментарии" class="text-white font-bold text-[16px] mb-3" />
              
              <FlexboxLayout flexDirection="row" alignItems="center" class="mb-4">
                <Image :src="currentUserAvatar || '~/assets/test1.png'" width="40" height="40" class="rounded-full"/>
                <TextField v-model="newCommentText" hint="Напишите, что думаете..." fontSize="12"
                  class="bg-[#1E1E1E] text-white rounded-2xl ml-3 px-4 py-2 flex-1" height="40"/>
                <Image src="~/assets/post.png" width="30" height="30" class="ml-2" @tap="addComment" />
              </FlexboxLayout>

              <StackLayout orientation="vertical">
                <StackLayout v-for="comment in commentsTree" :key="comment.id" class="mb-4">
                  <FlexboxLayout flexDirection="row" alignItems="flex-start">
                    <Image :src="toFullUrl(comment.avatar)" width="35" height="35" class="rounded-full mr-2"/>
                    <StackLayout class="flex-1">
                      <FlexboxLayout flexDirection="row" alignItems="center">
                        <Label :text="comment.user" class="text-white font-bold text-[12px]"/>
                        <Label :text="' ' + comment.time" class="text-[#C7C7C7] text-[10px] ml-2"/>
                      </FlexboxLayout>
                      <Label :text="comment.text" textWrap="true" class="text-white text-[13px] mt-1"/>
                      
                      <FlexboxLayout flexDirection="row" alignItems="center" class="mt-2">
                        <TextField v-model="replyTexts[comment.id]" hint="Ответить..." fontSize="10"
                          class="bg-[#1E1E1E] text-white rounded-xl px-3 py-1 flex-1" height="35"/>
                        <Image src="~/assets/post.png" width="20" height="20" class="ml-2" @tap="() => addReply(comment.id)" />
                      </FlexboxLayout>
                    </StackLayout>
                  </FlexboxLayout>

                  <StackLayout v-if="comment.replies && comment.replies.length" class="ml-8 mt-3">
                    <StackLayout v-for="reply in comment.replies" :key="reply.id" class="mb-3">
                      <FlexboxLayout flexDirection="row" alignItems="flex-start">
                        <Image :src="toFullUrl(reply.avatar)" width="30" height="30" class="rounded-full mr-2"/>
                        <StackLayout class="flex-1">
                          <FlexboxLayout flexDirection="row" alignItems="center">
                            <Label :text="reply.user" class="text-white font-bold text-[11px]"/>
                            <Label :text="' ' + reply.time" class="text-[#C7C7C7] text-[9px] ml-2"/>
                          </FlexboxLayout>
                          <Label :text="reply.text" textWrap="true" class="text-white text-[12px] mt-1"/>
                        </StackLayout>
                      </FlexboxLayout>
                    </StackLayout>
                  </StackLayout>
                </StackLayout>
              </StackLayout>
              
              <Label v-if="commentsTree.length === 0" text="Нет комментариев" class="text-[#C7C7C7] text-[14px] text-center mt-4" />
            </StackLayout>
          </StackLayout>
          
          <Label v-else text="Пост не найден" class="text-white text-center mt-10" />
        </FlexboxLayout>
      </ScrollView>

      <BottomNav row="1" col="0" :activeTab="activeTab" @update:activeTab="activeTab = $event" class="mb-2"/>

    </GridLayout>
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

.green-text {
  color: #479A0F;
}

.orange-text {
  color: #F25C05;
}

.text-center {
  text-align: center;
}
</style>