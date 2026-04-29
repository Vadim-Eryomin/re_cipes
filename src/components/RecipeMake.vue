<script lang="ts">
import { session } from '@nativescript/background-http';
import { isAvailable, requestPermissions, takePicture } from '@nativescript/camera';
import { Button, GridLayout, Image, ImageAsset, ImageSource, knownFolders, Label, path, ScrollView, StackLayout, TextField, TextView } from '@nativescript/core';
import { ImagePicker } from '@nativescript/imagepicker';
import * as imagePickerPlugin from '@nativescript/imagepicker'
import { defineComponent } from 'nativescript-vue';

type Ingredient = { name: string, amount: number, unit: string }
type Step = { photoAsset: ImageAsset | null, text: string, imagePath: string }

export default defineComponent({
    data() {
        return {
            steps: [{}, {}] as Step[],
            ingredients: [{}] as Ingredient[],
        }
    },
    methods: {
        uploadRecipe() {
            let s = session('upload-recipe');
            const task = s.multipartUpload([{ name: 'steps', value: JSON.stringify(this.steps) }, { name: 'ingredients', value: JSON.stringify(this.ingredients) }], {
                url: "http://10.0.2.2:5000/media/upload",
                method: "POST",
                headers: {
                    "Content-Type": "application/octet-stream"
                },
                description: "Uploading image from gallery"
            });
        },
        newIngredient() {
            this.ingredients.push({ name: '', amount: 0, unit: '' })

        },
        async onTakePicture(index: number) {
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

                    this.steps[index].photoAsset = asset;

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
                        description: "Uploading image from gallery"
                    });

                    // @ts-ignore
                    task.on('responded', e => this.steps[index].imagePath = e.data.url)

                } else {
                    console.log('Camera not available or permissions denied');
                }
            } catch (e: any) {
                console.error('Camera error:', e.message || e);
            }
        },

        async onChoosePicture(index: number) {
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
                    this.steps[index].photoAsset = selectedAsset;

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

                    task.on('responded', e => console.log(e.data))
                }
            } else {
                console.log('Разрешите доступ, иначе ничего не получится')
            }
        }
    }
});
</script>

<template>
    <Page>
        <ScrollView>
            <StackLayout>
                <StackLayout orientation="horizontal">
                    <Image src="~/assets/cross.png" class="w-16" />
                    <Label col="1" text="Новый рецепт" class="text-lg font-bold text-center text-[#F25C05]" />
                </StackLayout>
                <StackLayout>
                    <Image v-if="steps[0].photoAsset" :src="steps[0].photoAsset" class="w-[20rem] h-[10rem] rounded-lg">
                    </Image>

                    <StackLayout v-else="" class="bg-[#E9E9ED] p-3 rounded-lg h-[13rem] mx-4"
                        style="border-width: 3px; border-color: black; border-style: solid;" orientation="vertical">
                        <Image src="~/assets/gallery.png" class="w-[3rem]"></Image>
                        <Button class="bg-[#F25C05] text-white rounded-[50rem] mx-3 my-3 font-semibold"
                            @tap="onChoosePicture(0)">Выбрать фото из
                            галереи</Button>
                        <Button class="bg-[#969696] text-white rounded-[50rem] mx-3 font-semibold"
                            @tap="onTakePicture(0)">Сделать
                            снимок</Button>
                    </StackLayout>
                    <TextView v-model="steps[0].text" hint="Напишите что-нибудь..." class="mx-4 my-2 p-2" />
                </StackLayout>
                <StackLayout class="bg-[#E9E9ED] rounded-lg p-2 mt-10 mx-3">
                    <Label class="font-semibold text-xl text-center py-4">Ингредиенты</Label>
                    <StackLayout v-for="(item, index) in ingredients" class="my-2" orientation="horizontal">
                        <TextField class="p-2 mx-1 rounded text-md bg-[#fff] w-45" hint="Ингредиент">
                        </TextField>
                        <TextField class="p-2 mx-1 rounded text-md bg-[#fff]" hint="Сколько">
                        </TextField>
                        <TextField @tap.once="newIngredient" class="p-2 mx-1 rounded text-md bg-[#fff]" hint="Ед. изм.">
                        </TextField>
                    </StackLayout>
                </StackLayout>

                <StackLayout v-for="(item, index) in steps.slice(1)" orientation="horizontal">
                    <StackLayout orientation="horizontal" class="rounded-lg bg-[#E9E9ED] m-3">

                        <Image row="0" col="0" v-if="steps[index + 1].photoAsset" :src="steps[index + 1].photoAsset"
                            class="w-40 h-40 rounded-lg">
                        </Image>

                        <StackLayout row="0" col="0" v-else=""
                            class="bg-[#E9E9ED] p-3 rounded-lg h-[13rem] mx-4 w-50 bg-white pt-9"
                            style="border-width: 3px; border-color: black; border-style: solid;" orientation="vertical">
                            <Button class="bg-[#F25C05] text-white rounded-[50rem] mx-3 my-3 font-semibold"
                                @tap="onChoosePicture(index + 1)">Галерея</Button>
                            <Button class="bg-[#969696] text-white rounded-[50rem] mx-3 font-semibold"
                                @tap="onTakePicture(index + 1)">Фото</Button>
                        </StackLayout>

                        <TextView @tap.once="steps.push({ photoAsset: null, text: '', imagePath: '' })"
                            v-model="steps[index + 1].text" hint="Напишите, что делать на этом шаге..."
                            class="mx-4 my-2 p-2" />
                    </StackLayout>
                </StackLayout>
                <Button class="w-100 rounded-[50rem] font-bold text-lg bg-[#F25C05] text-white"
                    @tap="uploadRecipe">Опубликовать</Button>
            </StackLayout>
        </ScrollView>
    </Page>
</template>

<style>
* {
    android-elevation: 0;
}
</style>