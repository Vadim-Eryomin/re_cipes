<template>
    <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#E9E9ED]">
        <GridLayout rows="*" columns="*">
            
            <ScrollView row="0" col="0">
                <FlexboxLayout class="flex-col justify-center items-stretch h-full">
                    
                    <!-- Основной контейнер с отступами по бокам 16px -->
                    <GridLayout rows="auto" columns="*" class="bg-[#FFFFFF] rounded-2xl mx-4 py-11">
                        
                        <StackLayout class="px-4">
                            <!-- Логотип мини - отступ сверху 20 -->
                            <Image 
                                src="~/assets/logoMini.png" 
                                width="70" 
                                height="70"
                                class="self-center pt-4 mb-5"
                            />
                            
                            <!-- Заголовок -->
                            <Label text="С возвращением!" 
                                   class="text-[#F25C05] font-inter font-bold text-2xl text-center leading-9 mb-2" />
                            
                            <!-- Подзаголовок - отступ снизу 20 -->
                            <StackLayout class="self-center w-full mb-5">
                                <Label class="text-[#969696] font-inter font-semibold text-[16px] text-center leading-[27px]"
                                       text="Войдите в свой аккаунт для работы с reCipes"
                                       textWrap="true" 
                                       lineHeight="1" />
                            </StackLayout>
                            
                            <!-- Поля ввода -->
                            <StackLayout>
                                <!-- Email поле -->
                                <GridLayout rows="auto" columns="19, *, auto" 
                                        class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                        :class="[
                                            'border-5',
                                            focusedField === 'email' || form.email ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
                                        ]">
                                    
                                    <Image col="0" src="~/assets/email.png" 
                                        width="19" height="18" />
                                    
                                    <TextField col="1" 
                                            v-model="form.email"
                                            hint="E-mail"
                                            class="placeholder-[#969696] bg-transparent text-sm font-inter font-semibold ml-4"
                                            :class="form.email ? 'text-[#1E1D2E]' : 'text-[#969696]'"
                                            @focus="focusedField = 'email'"
                                            @blur="focusedField = null"
                                            autocorrect="false"
                                            autocapitalizationType="none" />
                                </GridLayout>

                                <!-- Пароль поле -->
                                <GridLayout rows="auto" columns="16, *, 20" 
                                        class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                        :class="[
                                            'border-5',
                                            focusedField === 'password' || form.password ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
                                        ]">
                                    
                                    <Image col="0" src="~/assets/key.png" 
                                        width="16" height="18" />
                                    
                                    <TextField col="1" 
                                            v-model="form.password"
                                            :secure="!showPassword"
                                            hint="Пароль"
                                            class="placeholder-[#969696] bg-transparent text-sm font-inter font-semibold ml-4"
                                            :class="form.password ? 'text-[#1E1D2E]' : 'text-[#969696]'"
                                            @focus="focusedField = 'password'"
                                            @blur="focusedField = null"
                                            autocorrect="false"
                                            autocapitalizationType="none" />
                                    
                                    <Image col="2" 
                                        :src="showPassword ? '~/assets/images/openeyes.png' : '~/assets/images/closeeyes.png'"
                                        :width="showPassword ? 24 : 18" 
                                        :height="showPassword ? 16 : 12" 
                                        @tap="togglePasswordVisibility" />
                                </GridLayout>
                                
                                <!-- Забыли пароль - отступы сверху и снизу 16 -->
                                <Label text="Забыли пароль?" 
                                       class="text-[#969696] font-inter font-semibold text-sm leading-[14px] text-right mb-4"
                                       @tap="onForgotPassword"/>
                                
                                <!-- Кнопка входа - изменена: убран h-14, добавлен py-4 для отступов 16px сверху и снизу -->
                                <Button text="Войти"
                                       class="rounded-2xl font-inter font-bold text-lg text-white px-4 py-4 mb-4"
                                       :class="isFormValid ? 'bg-[#F25C05]' : 'bg-[#969696]'"
                                       :isEnabled="isFormValid"
                                       textTransform="none"
                                       @tap="onLogin"/>
                                
                                <!-- Регистрация - отступ снизу 20 -->
                                <FlexboxLayout class="flex-row justify-center items-center">
                                    <Label text="Нет аккаунта?" 
                                           class="text-[#969696] font-inter font-semibold text-sm" />
                                    <Label text="Зарегистрироваться" 
                                           class="text-[#F25C05] font-inter font-semibold text-sm ml-8"
                                           @tap="goToRegistration" />
                                </FlexboxLayout>
                            </StackLayout>
                        </StackLayout>
                    </GridLayout>
                </FlexboxLayout>
            </ScrollView>
        </GridLayout>
    </Page>
</template>

<script lang="ts">
import { GridLayout, Image, Label, ScrollView, StackLayout } from '@nativescript/core';
import { ActionBar, defineComponent } from 'nativescript-vue';

export default defineComponent({
    data() {
        return {
            form: {
                email: '',
                password: ''
            },
            focusedField: null as string | null,
            showPassword: false
        };
    },
    computed: {
        isFormValid(): boolean {
            return this.form.email.trim() !== '' && this.form.password.trim() !== '';
        }
    },
    methods: {
        togglePasswordVisibility(): void {
            this.showPassword = !this.showPassword;
        },
        
        onLogin(): void {
            if (!this.isFormValid) return;
            console.log('Login clicked - переход на заглушку');
            this.$navigateTo(require('./StubScreen.vue').default, {
                transition: { 
                    name: 'slideLeft', 
                    duration: 300 
                },
                clearHistory: true
            });
        },
        
        onForgotPassword(): void {
            console.log('Forgot password clicked');
        },
        
        goToRegistration(): void {
            console.log('Navigating to Registration');
            this.$navigateTo(require('./Registration.vue').default, {
                transition: { 
                    name: 'fade', 
                    duration: 300 
                }
            });
        }
    }
});
</script>