<script lang="ts" setup>
import { GridLayout, Image, Label, ScrollView, StackLayout, TextField, FlexboxLayout } from '@nativescript/core';
import { ref, onMounted, computed } from "nativescript-vue"
import { $navigateTo } from 'nativescript-vue'
import Recipe from './Recipe.vue';
import BottomNav from './BottomNav.vue';
import { samplePosts, type Post } from './data/posts';

const posts = ref<Post[]>(samplePosts)
const searchQuery = ref('')
const showSearchResults = ref(false)
const activeTab = ref('main')

function getTopicName(topic: string): string {
  return topic.replace(/^r\//, '').toLowerCase()
}

const uniqueTopics = computed(() => {
  const topicsMap = new Map<string, number>()
  posts.value.forEach(post => {
    const count = topicsMap.get(post.topic) || 0
    topicsMap.set(post.topic, count + 1)
  })
  return Array.from(topicsMap.entries()).map(([topic, count]) => ({ topic, count })).sort((a, b) => 
    a.topic.localeCompare(b.topic)
  )
})

const filteredTopics = computed(() => {
  if (!searchQuery.value) {
    return uniqueTopics.value
  }
  const query = searchQuery.value.toLowerCase()
  return uniqueTopics.value.filter(item => 
    getTopicName(item.topic).startsWith(query)
  )
})

const filteredPosts = computed(() => {
  if (!searchQuery.value) {
    return posts.value
  }
  const query = searchQuery.value.toLowerCase()
  return posts.value.filter(post => 
    getTopicName(post.topic).startsWith(query)
  )
})

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

function voteUp(postId: string) {
  const post = posts.value.find(p => p.id === postId)
  if (!post) return

  if (post.userLiked) {
    post.likes--
    post.userLiked = false
  } else {
    if (post.userDisliked) {
      post.likes++
      post.userDisliked = false
    }
    post.likes++
    post.userLiked = true
  }
}

function voteDown(postId: string) {
  const post = posts.value.find(p => p.id === postId)
  if (!post) return

  if (post.userDisliked) {
    post.likes++
    post.userDisliked = false
  } else {
    if (post.userLiked) {
      post.likes--
      post.userLiked = false
    }
    post.likes--
    post.userDisliked = true
  }
}

function goToRecipe(postId: string) {
  $navigateTo(Recipe, {
    props: { postId },
    transition: { name: "slideLeft" }
  })
}

function onSearchChange(args: any) {
  searchQuery.value = args.value
  showSearchResults.value = args.value.length > 0
}

function selectTopic(topic: string) {
  const topicName = getTopicName(topic)
  searchQuery.value = topicName
  showSearchResults.value = false
}

onMounted(() => {
})
</script>

<template>
  <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
    <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
      
      <ScrollView row="0" col="0">
        <FlexboxLayout flexDirection="column" alignItems="stretch" class="px-4 pt-8 pb-4">
          
          <StackLayout orientation="horizontal" verticalAlignment="center" class="mt-2 mb-2">
            <Image class="" height="30" src="~/assets/name_mini.png" />
            <GridLayout class="bg-[#393939] rounded-lg ml-2 mr-0" columns="auto,*" height="40" verticalAlignment="center">
              <Image col="0" src="~/assets/Search_main.png" class="ml-2" width="25" height="25" />
              <TextField col="1" hint="Поиск в reCipes" class="ml-1 search-input text-white text-[14px] custom-hint" editable="true" 
                @textChange="onSearchChange" :text="searchQuery" />
            </GridLayout>
          </StackLayout>

          <StackLayout v-if="showSearchResults && filteredTopics.length > 0" class="bg-[#1E1E1E] rounded-xl mb-4">
            <Label text="Топики" class="text-[#C7C7C7] text-[12px] px-4 pt-3 pb-1" />
            <StackLayout v-for="item in filteredTopics" :key="item.topic" 
              @tap="() => selectTopic(item.topic)" class="px-4 py-3 border-b border-[#393939]">
              <FlexboxLayout flexDirection="row" justifyContent="space-between" alignItems="center" width="100%">
                <Label :text="item.topic" class="text-white text-[14px] font-medium" />
                <Label :text="item.count + ' ' + (item.count === 1 ? 'пост' : (item.count >= 2 && item.count <= 4 ? 'поста' : 'постов'))" 
                  class="text-[#C7C7C7] text-[12px]" />
              </FlexboxLayout>
            </StackLayout>
          </StackLayout>

          <StackLayout v-for="(post, index) in filteredPosts" :key="post.id">
            <StackLayout class="mb-4">
              <GridLayout columns="auto, *, auto" class="mx-4 mt-3 ml-0 mr-0" verticalAlignment="center">
                <Image col="0" width="40" height="40" :src="toFullUrl(post.userAvatar)" class="rounded-full" />
                
                <StackLayout col="1" class="ml-2" verticalAlignment="center">
                  <Label :text="post.topic" class="text-white font-bold text-[12px]" />
                  <Label :text="post.userName" class="text-white text-[12px]" />
                </StackLayout>
                
                <Label col="2" :text="post.date" class="text-[#C7C7C7] text-[12px] font-normal text-right " />
              </GridLayout>

              <Label :text="post.title" class="text-white text-[15px] mx-4 mt-2 ml-0 mr-0" textWrap="true" @tap="() => goToRecipe(post.id)" />
              
              <Image v-if="post.image" class="mx-2 mt-2 rounded-xl" :src="toFullUrl(post.image)" width="100%" @tap="() => goToRecipe(post.id)" />

              <StackLayout orientation="horizontal" verticalAlignment="center" class="mx-4 mt-2 ml-0">
                <StackLayout class="bg-[#121212] rounded-4xl border border-[#393939]" orientation="horizontal" height="30" verticalAlignment="center">
                  <Image :src="post.userLiked ? '~/assets/arrow_up.png' : '~/assets/arrow_up (1).png'" class="ml-3" width="30" height="30" @tap="() => voteUp(post.id)" />
                  <Label :text="formatVotes(post.likes)"
                    :class="['mx-2 text-center', voteColor(post.likes)]" width="32" />
                  <Image :src="post.userDisliked ? '~/assets/arrow_down.png' : '~/assets/arrow_down (1).png'" class="mr-3" width="30" height="30" @tap="() => voteDown(post.id)" />
                </StackLayout>

                <StackLayout class="bg-[#121212] rounded-4xl ml-3 border border-[#393939]" orientation="horizontal" height="30"
                  verticalAlignment="center" @tap="() => goToRecipe(post.id)">
                  <Image src="~/assets/Chat_alt.png" class="ml-3" width="20" height="20" color="white" />
                  <Label :text="post.comments.toString()" class="search-input ml-2 mr-3 text-white" />
                </StackLayout>
              </StackLayout>
            </StackLayout>

            <StackLayout v-if="index < filteredPosts.length - 1" height="1" backgroundColor="#393939" />
          </StackLayout>

          <Label v-if="filteredPosts.length === 0 && !showSearchResults && searchQuery" 
            text="Нет постов в этом топике" 
            class="text-[#C7C7C7] text-[14px] text-center mt-10" />
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

.custom-hint {
  placeholder-color: #898989;
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

.bg-gray {
  background-color: #E9E9ED;
}

.border-b {
  border-bottom-width: 1;
}
</style>