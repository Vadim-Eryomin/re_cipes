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
    ImageSource,
    knownFolders,
    path
} from '@nativescript/core';
import { session } from '@nativescript/background-http';
import { isAvailable, requestPermissions, takePicture } from '@nativescript/camera';
import { ImagePicker } from '@nativescript/imagepicker';
import * as imagePickerPlugin from '@nativescript/imagepicker';
import { ref } from "nativescript-vue";
import BottomNav from './BottomNav.vue';

type Ingredient = { name: string, amount: string, unit: string }
type Step = { photoAsset: any | null, text: string, imagePath: string }

const steps = ref<Step[]>([{ photoAsset: null, text: '', imagePath: '' }, { photoAsset: null, text: '', imagePath: '' }])
const ingredients = ref<Ingredient[]>([{ name: '', amount: '', unit: '' }])
const activeTab = ref('create')
const recipeTitle = ref('')
const recipeDescription = ref('')
const topicName = ref('')

function uploadRecipe() {
    let s = session('upload-recipe');
    const task = s.multipartUpload([
        { name: 'title', value: recipeTitle.value },
        { name: 'description', value: recipeDescription.value },
        { name: 'topic', value: topicName.value },
        { name: 'steps', value: JSON.stringify(steps.value) }, 
        { name: 'ingredients', value: JSON.stringify(ingredients.value) }
    ], {
        url: "http://10.0.2.2:5000/posts",
        method: "POST",
        headers: {
            "Content-Type": "application/octet-stream"
        },
        description: "Uploading recipe data"
    });
}

function newIngredient() {
    ingredients.value.push({ name: '', amount: '', unit: '' })
}

function removeMainPhoto() {
    steps.value[0].photoAsset = null
    steps.value[0].imagePath = ''
}

function removeStepPhoto(index: number) {
    steps.value[index].photoAsset = null
    steps.value[index].imagePath = ''
}

async function onTakePicture(index: number) {
    try {
        const perms = await requestPermissions();

        if (perms && isAvailable()) {
            const asset = await takePicture({
                width: 1280,
                height: 720,
                keepAspectRatio: true,
                saveToGallery: false,
                cameraFacing: 'rear'
            });

            steps.value[index].photoAsset = asset;

            let source = await ImageSource.fromAsset(asset);
            let temp = knownFolders.temp();
            let filepath = path.join(temp.path, `photo_${Date.now()}.jpg`);
            await source.saveToFileAsync(filepath, 'jpg');

            let s = session('upload-image');
            const task = s.multipartUpload([{ name: 'file', filename: filepath, mimeType: 'image/jpeg' }], {
                url: "http://10.0.2.2:5000/media/upload",
                method: "POST",
                headers: {
                    "Content-Type": "application/octet-stream"
                },
                description: "Uploading image from camera"
            });

            task.on('responded', (e: any) => {
                if (e.data && typeof e.data === 'object' && e.data.url) {
                    steps.value[index].imagePath = e.data.url
                } else if (typeof e.data === 'string') {
                    steps.value[index].imagePath = e.data
                }
            })

        } else {
            console.log('Camera not available or permissions denied');
        }
    } catch (e: any) {
        console.error('Camera error:', e.message || e);
    }
}

async function onChoosePicture(index: number) {
    let imagePickerObj: ImagePicker = imagePickerPlugin.create({
        mode: 'single',
        android: { use_photo_picker: true },
    })

    let authResult = await imagePickerObj.authorize()
    if (authResult.authorized) {
        let selection = await imagePickerObj.present()
        if (!!selection.at(0)) {
            let selectedAsset = selection.at(0)!.asset
            let source = await ImageSource.fromAsset(selectedAsset);
            steps.value[index].photoAsset = selectedAsset;

            let temp = knownFolders.temp();
            let filepath = path.join(temp.path, `chosen_photo_${Date.now()}.jpg`);
            await source.saveToFileAsync(filepath, 'jpg');
            console.log('Изображение сохранено по пути:', filepath);

            let s = session('upload-image');
            const task = s.multipartUpload([{ name: 'file', filename: filepath, mimeType: 'image/jpeg' }], {
                url: "http://10.0.2.2:5000/media/upload",
                method: "POST",
                headers: {
                    "Content-Type": "application/octet-stream"
                },
                description: "Uploading image from gallery"
            });

            task.on('responded', (e: any) => {
                if (e.data && typeof e.data === 'object' && e.data.url) {
                    steps.value[index].imagePath = e.data.url
                } else if (typeof e.data === 'string') {
                    steps.value[index].imagePath = e.data
                }
                console.log(e.data)
            })
        }
    } else {
        console.log('Разрешите доступ, иначе ничего не получится')
    }
}

function addStep() {
    steps.value.push({ photoAsset: null, text: '', imagePath: '' })
}
</script>

<template>
    <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
        <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
            
            <ScrollView row="0" col="0">
                <FlexboxLayout flexDirection="column" alignItems="stretch" class="px-4 pt-8 pb-24">
                    
                    <Label text="Новый рецепт" class="text-[#F25C05] text-lg font-bold mb-4 text-left" />

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Название рецепта *" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <TextField v-model="recipeTitle" 
                            hint="Введите название..." 
                            class="bg-[#121212] text-white rounded-xl px-3 py-2 text-[14px]" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Топик *" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <TextField v-model="topicName" 
                            hint="r/ваш_топик" 
                            class="bg-[#121212] text-white rounded-xl px-3 py-2 text-[14px]" />
                        <Label text="Например: r/выпечка, r/завтраки" 
                            class="text-[#C7C7C7] text-[10px] mt-1" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Описание (необязательно)" class="text-[#C7C7C7] text-[12px] mb-2" />
                        <TextView v-model="recipeDescription" 
                            hint="Расскажите подробнее о вашем рецепте..." 
                            class="bg-[#121212] text-white rounded-xl p-3 text-[14px]" 
                            height="100" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Фото блюда" class="text-[#C7C7C7] text-[12px] mb-3" />
                        
                        <GridLayout v-if="steps[0].photoAsset" rows="auto" columns="*" class="mb-3">
                            <Image row="0" col="0" :src="steps[0].photoAsset" 
                                class="w-full h-48 rounded-xl" stretch="aspectFill" />
                            <Button row="0" col="0" text="✕" @tap="removeMainPhoto" textTransform="none"
                                class="bg-[#F25C05] text-white rounded-full absolute-center" width="40" height="40" />
                        </GridLayout>
                        
                        <FlexboxLayout v-else flexDirection="column" alignItems="center" justifyContent="center"
                            class="bg-[#121212] rounded-xl p-4 h-48">
                            <Button @tap="onChoosePicture(0)" textTransform="none"
                                class="bg-[#F25C05] text-white rounded-3xl px-6 py-2 font-semibold text-[14px] mb-2">
                                Выбрать фото из галереи
                            </Button>
                            <Button @tap="onTakePicture(0)" textTransform="none"
                                class="bg-[#393939] text-white rounded-3xl px-6 py-2 font-semibold text-[14px]">
                                Сделать снимок
                            </Button>
                        </FlexboxLayout>
                        
                        <TextView v-model="steps[0].text" 
                            hint="Краткое описание блюда..." 
                            class="bg-[#121212] text-white rounded-xl p-3 mt-3 text-[14px]" 
                            height="80" />
                    </StackLayout>

                    <StackLayout class="bg-[#1E1E1E] rounded-2xl p-4 mb-4">
                        <Label text="Ингредиенты" class="text-white text-center font-bold text-[16px] mb-3" />
                        
                        <FlexboxLayout v-for="(item, index) in ingredients" :key="index" 
                            flexDirection="row" alignItems="center" class="mb-2">
                            <TextField v-model="item.name" hint="Ингредиент" 
                                class="bg-[#121212] text-white rounded-xl px-3 py-2 flex-1 mr-2 text-[14px]" />
                            <TextField v-model="item.amount" hint="Сколько" keyboardType="number"
                                class="bg-[#121212] text-white rounded-xl px-3 py-2 w-20 mr-2 text-[14px]" />
                            <TextField v-model="item.unit" hint="Ед. изм." 
                                class="bg-[#121212] text-white rounded-xl px-3 py-2 w-20 text-[14px]" />
                        </FlexboxLayout>
                        
                        <Button @tap="newIngredient" textTransform="none"
                            class="bg-[#393939] text-white rounded-xl px-4 py-2 text-[14px] mt-2">
                            + Добавить ингредиент
                        </Button>
                    </StackLayout>

                    <StackLayout v-for="(item, index) in steps.slice(1)" :key="index" 
                        class="bg-[#1E1E1E] rounded-2xl p-4 mb-3">
                        <Label :text="'Шаг ' + (index + 1)" class="text-[#F25C05] font-bold text-[14px] mb-2" />
                        
                        <FlexboxLayout flexDirection="row" class="mb-3">
                            <StackLayout width="40%" class="mr-3">
                                <GridLayout v-if="steps[index + 1].photoAsset" rows="auto" columns="*">
                                    <Image row="0" col="0" :src="steps[index + 1].photoAsset" 
                                        class="w-full h-24 rounded-xl mb-1" stretch="aspectFill" />
                                    <Button row="0" col="0" text="✕" @tap="removeStepPhoto(index + 1)" textTransform="none"
                                        class="bg-[#F25C05] text-white rounded-full absolute-center" width="32" height="32" />
                                </GridLayout>
                                
                                <FlexboxLayout v-else flexDirection="column" alignItems="center" justifyContent="center"
                                    class="bg-[#121212] rounded-xl w-full h-24">
                                    <Button @tap="onChoosePicture(index + 1)" textTransform="none"
                                        class="bg-[#F25C05] text-white rounded-xl px-2 py-1 text-[10px] mb-1">
                                        Галерея
                                    </Button>
                                    <Button @tap="onTakePicture(index + 1)" textTransform="none"
                                        class="bg-[#393939] text-white rounded-xl px-2 py-1 text-[10px]">
                                        Фото
                                    </Button>
                                </FlexboxLayout>
                            </StackLayout>
                            
                            <TextView v-model="steps[index + 1].text" 
                                hint="Напишите, что делать на этом шаге..." 
                                class="bg-[#121212] text-white rounded-xl p-3 flex-1 text-[14px]" 
                                height="96" />
                        </FlexboxLayout>
                    </StackLayout>

                    <Button @tap="addStep" textTransform="none"
                        class="bg-[#393939] text-white rounded-xl px-4 py-3 text-[14px] mb-4">
                        + Добавить шаг
                    </Button>

                    <Button @tap="uploadRecipe" textTransform="none"
                        class="bg-[#F25C05] text-white rounded-3xl py-3 font-bold text-[16px]">
                        Опубликовать
                    </Button>
                    
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

.absolute-center {
    horizontal-align: center;
    vertical-align: middle;
}
</style>