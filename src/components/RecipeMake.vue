<script lang="ts">
import { session } from '@nativescript/background-http';
import { isAvailable, requestPermissions, takePicture } from '@nativescript/camera';
import { ImageSource, knownFolders, path, ImageAsset } from '@nativescript/core';
import * as imagePickerPlugin from '@nativescript/imagepicker';
import { defineComponent } from 'nativescript-vue';
import { API_BASE_URL } from '~/config';
import { AjaxService } from '~/features/core/ajaxService';

type Ingredient = { name: string; amount: number; unit: string };
type Step = { photoAsset: ImageAsset | null; text: string; imagePath: string };

const ajax = new AjaxService(API_BASE_URL);

export default defineComponent({
  data() {
    return {
      steps: [{ photoAsset: null, text: '', imagePath: '' }] as Step[],
      ingredients: [{ name: '', amount: 0, unit: '' }] as Ingredient[],
    };
  },
  methods: {
    async uploadRecipe() {
      const firstBlock = this.steps[0];
      const actualSteps = this.steps.slice(1);

      const payload = {
        text: firstBlock?.text || '', 
        
        medias: firstBlock?.imagePath ? [firstBlock.imagePath] : [],

        recipe: actualSteps.map((s) => ({
          step: s.text,
          media: s.imagePath || '',
        })),

        ingredients: this.ingredients
          .filter(i => i.name.trim() !== '')
          .map((i) => ({
            name: i.name,
            count: Number(i.amount),
            measure_name: i.unit,
          })),
        
        community: 'general'
      };

      try {
        const result = await ajax.post({ url: '/posts', data: payload });
        console.log('Успех', result);
      } catch (e) {
        console.error('Ошибка при публикации', e);
      }
    },

    newIngredient() {
      this.ingredients.push({ name: '', amount: 0, unit: '' });
    },

    async handleImageUpload(filepath: string, index: number) {
      let s = session('upload-image');
      const task = s.multipartUpload(
        [{ name: 'file', filename: filepath, mimeType: 'image/jpeg' }],
        {
          url: API_BASE_URL + '/media/upload',
          method: 'POST',
          headers: { 'Content-Type': 'application/octet-stream' },
          description: 'Uploading image',
        }
      );

      task.on('responded', (e) => {
        const responseData = JSON.parse(e.data);
        this.steps[index].imagePath = responseData.url;
        console.log(`Фото для блока ${index} загружено:`, responseData.url);
      });
      
      task.on('error', (e) => console.error('Ошибка загрузки файла', e));
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
          });

          this.steps[index].photoAsset = asset;
          let source = await ImageSource.fromAsset(asset);
          let filepath = path.join(knownFolders.temp().path, `photo_${Date.now()}.jpg`);
          await source.saveToFileAsync(filepath, 'jpg');

          await this.handleImageUpload(filepath, index);
        }
      } catch (e: any) {
        console.error('Camera error:', e.message || e);
      }
    },

    async onChoosePicture(index: number) {
      let imagePickerObj = imagePickerPlugin.create({
        mode: 'single',
        android: { use_photo_picker: true },
      });

      let authResult = await imagePickerObj.authorize();
      if (authResult.authorized) {
        let selection = await imagePickerObj.present();
        if (selection.length > 0) {
          let selectedAsset = selection[0].asset;
          this.steps[index].photoAsset = selectedAsset;

          let source = await ImageSource.fromAsset(selectedAsset);
          let filepath = path.join(knownFolders.temp().path, `chosen_${Date.now()}.jpg`);
          await source.saveToFileAsync(filepath, 'jpg');

          await this.handleImageUpload(filepath, index);
        }
      }
    },
    
    addStep() {
        this.steps.push({ photoAsset: null, text: '', imagePath: '' });
    }
  },
});
</script>

<template>
  <Page>
    <ScrollView>
      <StackLayout class="p-4">
        <StackLayout orientation="horizontal" class="mb-4">
          <Image src="~/assets/cross.png" class="w-8 h-8" />
          <Label text="Новый рецепт" class="text-xl font-bold text-[#F25C05] ml-4" />
        </StackLayout>

        <StackLayout class="mb-6">
          <Image v-if="steps[0].photoAsset" :src="steps[0].photoAsset" class="w-full h-48 rounded-lg mb-2" stretch="aspectFill" />
          <StackLayout v-else class="bg-[#E9E9ED] p-8 rounded-lg border-2 border-dashed border-gray-400 items-center">
            <Button text="Галерея" @tap="onChoosePicture(0)" class="bg-[#F25C05] text-white rounded-full p-2 w-40 mb-2" />
            <Button text="Камера" @tap="onTakePicture(0)" class="bg-[#969696] text-white rounded-full p-2 w-40" />
          </StackLayout>
          <TextView v-model="steps[0].text" hint="Краткое описание рецепта..." class="bg-white p-4 rounded-lg mt-2" />
        </StackLayout>

        <StackLayout class="bg-[#E9E9ED] rounded-lg p-4 mb-6">
          <Label text="Ингредиенты" class="font-bold text-lg text-center mb-4" />
          <StackLayout v-for="(item, index) in ingredients" :key="index" orientation="horizontal" class="mb-2">
            <TextField v-model="item.name" class="bg-white p-2 rounded w-1/2 mr-1" hint="Название" />
            <TextField v-model="item.amount" keyboardType="number" class="bg-white p-2 rounded w-1/4 mr-1" hint="Кол-во" />
            <TextField v-model="item.unit" @focus="index === ingredients.length - 1 && newIngredient()" class="bg-white p-2 rounded w-1/4" hint="Ед. изм." />
          </StackLayout>
        </StackLayout>

        <Label text="Шаги приготовления" class="font-bold mb-2" />
        <StackLayout v-for="(item, index) in steps.slice(1)" :key="index" class="bg-[#E9E9ED] p-4 rounded-lg mb-4">
          <GridLayout columns="120, *" rows="auto">
             <StackLayout col="0">
                <Image v-if="steps[index + 1].photoAsset" :src="steps[index + 1].photoAsset" class="w-24 h-24 rounded-lg" stretch="aspectFill" />
                <Button v-else text="Фото" @tap="onChoosePicture(index + 1)" class="bg-gray-400 text-xs text-white" />
             </StackLayout>
             <TextView col="1" v-model="steps[index + 1].text" hint="Что нужно сделать?" class="bg-white p-2 rounded-lg ml-2" />
          </GridLayout>
        </StackLayout>
        
        <Button text="+ Добавить шаг" @tap="addStep" class="text-[#F25C05] mb-4" />

        <Button text="Опубликовать" @tap="uploadRecipe" class="bg-[#F25C05] text-white font-bold p-4 rounded-full" />
      </StackLayout>
    </ScrollView>
  </Page>
</template>

<style>
* {
    android-elevation: 0;
}
</style>