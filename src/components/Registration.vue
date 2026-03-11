<template>
    <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#E9E9ED]">
        <GridLayout rows="*" columns="*">
            
            <ScrollView row="0" col="0">
                <FlexboxLayout class="flex-col justify-center items-stretch h-full">
                    
                    <!-- Основной контейнер с отступами по бокам 16px -->
                    <GridLayout rows="auto" columns="*" class="bg-[#FFFFFF] rounded-2xl mx-4 py-11">
                        
                        <StackLayout class="px-4">
                            <!-- Логотип мини -->
                            <Image 
                                src="~/assets/logoMini.png" 
                                width="70" 
                                height="70"
                                class="self-center pt-5 mb-5"
                            />
                            
                            <!-- Заголовок -->
                            <Label text="Добро пожаловать!" 
                                   class="text-[#F25C05] font-inter font-bold text-2xl text-center leading-9 mb-2" />
                            
                            <!-- Подзаголовок -->
                            <StackLayout class="self-center w-full mb-5">
                                <Label class="text-[#969696] font-inter font-semibold text-[16px] text-center leading-[27px]"
                                       text="Заполните данные о себе для создания аккаунта в reCipes"
                                       textWrap="true" 
                                       lineHeight="1" />
                            </StackLayout>
                            
                            <!-- Поля ввода -->
                            <StackLayout>
                                <!-- ФИО поле -->
                                <GridLayout rows="auto" columns="19, *, auto" 
                                           class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                           :class="[
                                               'border-5',
                                               focusedField === 'fullname' ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
                                           ]">
                                    
                                    <Image col="0" src="~/assets/profile.png" 
                                           width="14" height="18" />
                                    
                                    <TextField col="1" 
                                              v-model="form.fullname"
                                              hint="Имя пользователя"
                                              class="placeholder-[#969696] bg-transparent text-sm font-inter font-semibold ml-4"
                                              :class="form.fullname ? 'text-[#1E1D2E]' : 'text-[#969696]'"
                                              @focus="focusedField = 'fullname'"
                                              @blur="focusedField = null"
                                              autocorrect="false"
                                              autocapitalizationType="words" />
                                </GridLayout>
                                
                                <!-- Email поле -->
                                <GridLayout rows="auto" columns="19, *, auto" 
                                           class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                           :class="[
                                               'border-5',
                                               focusedField === 'email' ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
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
                                              autocapitalizationType="none"
                                              keyboardType="email" />
                                </GridLayout>
                                
                                <!-- Пароль поле -->
                                <GridLayout rows="auto" columns="16, *, 20" 
                                           class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                           :class="[
                                               'border-5',
                                               focusedField === 'password' ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
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
                                          @tap="togglePasswordVisibility('password')" />
                                </GridLayout>
                                
                                <!-- Подтверждение пароля поле -->
                                <GridLayout rows="auto" columns="16, *, 20" 
                                           class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                                           :class="[
                                               'border-5',
                                               focusedField === 'confirmPassword' ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
                                           ]">
                                    
                                    <Image col="0" src="~/assets/key.png" 
                                           width="16" height="18" />
                                    
                                    <TextField col="1" 
                                              v-model="form.confirmPassword"
                                              :secure="!showConfirmPassword"
                                              hint="Подтверждение пароля"
                                              class="placeholder-[#969696] bg-transparent text-sm font-inter font-semibold ml-4"
                                              :class="form.confirmPassword ? 'text-[#1E1D2E]' : 'text-[#969696]'"
                                              @focus="focusedField = 'confirmPassword'"
                                              @blur="focusedField = null"
                                              autocorrect="false"
                                              autocapitalizationType="none" />
                                    
                                    <Image col="2" 
                                          :src="showConfirmPassword ? '~/assets/images/openeyes.png' : '~/assets/images/closeeyes.png'"
                                          :width="showConfirmPassword ? 24 : 18" 
                                          :height="showConfirmPassword ? 16 : 12" 
                                          @tap="togglePasswordVisibility('confirmPassword')" />
                                </GridLayout>
                                
                                <!-- Кнопка регистрации -->
                                <Button text="Зарегистрироваться"
                                       class="rounded-2xl font-inter font-bold text-lg text-white px-4 py-4 mt-4"
                                       :class="isFormValid ? 'bg-[#F25C05]' : 'bg-[#969696]'"
                                       :isEnabled="isFormValid"
                                       textTransform="none"
                                       @tap="onRegister"/>
                                
                                <!-- Вход для существующих пользователей - цвет 969696 -->
                                <FlexboxLayout class="flex-row justify-center items-center mt-6">
                                    <Label text="Уже есть аккаунт?" 
                                           class="text-[#969696] font-inter font-semibold text-sm" />
                                    <Label text="Войти" 
                                           class="text-[#F25C05] font-inter font-semibold text-sm ml-8"
                                           @tap="goToLogin" />
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
import { defineComponent } from 'nativescript-vue';

interface FormData {
    fullname: string;
    email: string;
    password: string;
    confirmPassword: string;
}

export default defineComponent({
    data() {
        return {
            form: {
                fullname: '',
                email: '',
                password: '',
                confirmPassword: ''
            } as FormData,
            focusedField: null as string | null,
            showPassword: false,
            showConfirmPassword: false
        };
    },
    computed: {
        isFormValid(): boolean {
            // Простая проверка на заполненность полей
            return this.form.fullname.trim() !== '' && 
                   this.form.email.trim() !== '' && 
                   this.form.password.trim() !== '' && 
                   this.form.confirmPassword.trim() !== '';
        }
    },
    methods: {
        togglePasswordVisibility(field: string): void {
            if (field === 'password') {
                this.showPassword = !this.showPassword;
            } else {
                this.showConfirmPassword = !this.showConfirmPassword;
            }
        },
        
        onRegister(): void {
            if (!this.isFormValid) {
                return;
            }
            
            console.log('Registration successful for:', this.form.email);
            console.log('Redirecting to Main screen');
            
            this.$navigateTo(require('./Main.vue').default, {
                transition: {
                    name: 'slideLeft',
                    duration: 300
                },
                clearHistory: true
            });
        },
        
        goToLogin(): void {
            console.log('Navigating to Login');
            this.$navigateTo(require('./Login.vue').default, {
                transition: {
                    name: 'fade',
                    duration: 300
                }
            });
        }
    }
});
</script>