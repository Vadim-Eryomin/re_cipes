<template>
  <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#121212]">
    <GridLayout rows="*, auto" columns="*" class="bg-[#121212]">
      
      <ScrollView row="0" col="0">
        <FlexboxLayout flexDirection="column" justifyContent="flex-start" alignItems="stretch" class="px-4 pt-8 pb-4">
          
          <Image src="~/assets/logo.png" 
                 width="40" height="40" 
                 class="self-center mb-2.5" />
          
          <Label text="Введите почту и&nbsp;пароль"
                 class="text-white font-inter font-extrabold text-2xl text-center"
                 textWrap="true" />
          
          <StackLayout class="mt-5">
            <FlexboxLayout flexDirection="row" justifyContent="center" alignItems="center" flexWrap="wrap">
              <Label class="text-white font-inter font-semibold text-base" text="чтобы войти в " />
              <Label class="text-[#F25C05] font-inter font-semibold text-base" text="ReCipes" />
            </FlexboxLayout>
          </StackLayout>

          <StackLayout class="mt-6">
            <GridLayout rows="auto" columns="16, *" 
                       class="rounded-xl px-4 min-h-14 items-center pt-1"
                       :class="[
                           focusedField === 'email' ? 'border-[#F25C05] border-5' : 'border-[#121212] border-5',
                           errors.email && touched.email ? 'border-[#3D2519] border-5 bg-[#3D2519]' : 'bg-[#252525]'
                       ]">
              
              <Image col="0" src="~/assets/email.png" width="20" height="16" class="self-center" />
              
              <StackLayout col="1" class="ml-4 py-2">
                <Label text="E-mail" 
                       class="font-inter font-semibold text-xs mb-1"
                       :class="errors.email && touched.email ? 'text-[#DE6C35]' : 'text-[#B2B6B8]'" />
                <TextField v-model="form.email"
                          hint="test@mail.ru"
                          class="text-white font-inter font-medium text-sm bg-transparent p-0"
                          color="white"
                          @focus="focusedField = 'email'"
                          @blur="onBlur('email')"
                          @textChange="onEmailChange"
                          autocorrect="false"
                          autocapitalizationType="none" />
              </StackLayout>
            </GridLayout>
            <Label v-if="errors.email && touched.email"
                   :text="errors.email"
                   class="text-[#DE6C35] font-inter text-xs ml-4 mt-1" />

            <GridLayout rows="auto" columns="16, *, auto" 
                       class="mt-4 rounded-xl px-4 min-h-14 items-center pt-1"
                       :class="[
                           focusedField === 'password' ? 'border-[#F25C05] border-5' : 'border-[#121212] border-5',
                           errors.password && touched.password ? 'border-[#3D2519] border-5 bg-[#3D2519]' : 'bg-[#252525]'
                       ]">
              
              <Image col="0" src="~/assets/key.png" width="16" height="18" class="self-center" />
              
              <StackLayout col="1" class="ml-4 py-2">
                <Label text="Пароль" 
                       class="font-inter font-semibold text-xs mb-1"
                       :class="errors.password && touched.password ? 'text-[#DE6C35]' : 'text-[#B2B6B8]'" />
                <TextField v-model="form.password"
                          :secure="!showPassword"
                          hint="123456"
                          hintColor="#BEBEBE"
                          class="text-white font-inter font-normal text-sm bg-transparent p-0"
                          style="font-size: 14px; height: 18;"
                          color="white"
                          @focus="focusedField = 'password'"
                          @blur="onBlur('password')"
                          @textChange="onPasswordChange"
                          autocorrect="false"
                          autocapitalizationType="none" />
              </StackLayout>

              <Label v-if="form.password.length > 0"
                    col="2"
                    :text="showPassword ? 'Скрыть' : 'Показать'"
                    fontSize="12"
                    color="#F25C05"
                    class="font-inter font-semibold text-right mr-0"
                    @tap="togglePasswordVisibility" />
            </GridLayout>

            <Label v-if="errors.password && touched.password"
                   :text="errors.password"
                   class="text-[#DE6C35] font-inter text-xs ml-4 mt-1" />

            <GridLayout class="mt-4" @tap="onForgotPassword">
              <Label text="Забыли пароль?"
                     class="text-[#B2B6B8] font-inter font-semibold text-sm leading-5 text-right py-2 px-2" />
            </GridLayout>
          </StackLayout>
        </FlexboxLayout>
      </ScrollView>

      <GridLayout row="1" col="0" rows="auto" columns="*" class="px-4 pb-4">
        <StackLayout>
          <FlexboxLayout flexDirection="row" justifyContent="center" alignItems="center" class="mb-4">
            <Label text="Нет аккаунта?"
                   class="text-[#B2B6B8] font-inter font-semibold text-sm leading-5" 
                   textWrap="true"/>
            
            <Label text="Зарегистрироваться"
                   class="text-[#F25C05] font-inter font-semibold text-sm leading-5 ml-8 py-2 px-2"
                   @tap="goToRegistration" />
          </FlexboxLayout>
          
          <ActivityIndicator v-if="isLoading" :busy="true" color="#F25C05" class="mb-4" />
          
          <Button v-else
              text="Войти"
              textTransform="none"
              :class="['h-14 rounded-xl font-inter font-semibold text-base text-white w-full mb-4',
                        isFormValid && !isLoading ? 'bg-[#F25C05]' : 'bg-[#969696]']"
              :isEnabled="isFormValid && !isLoading"
              @tap="onLogin" />
      </StackLayout>
      </GridLayout>

      <GridLayout v-if="showErrorModal"
                 row="0" col="0" rowSpan="2"
                 backgroundColor="#818181" opacity="0.64"
                 @tap="closeErrorModal"
                 zIndex="1000" />

      <GridLayout v-if="showErrorModal" 
                 row="0" col="0" rowSpan="2"
                 horizontalAlignment="stretch" verticalAlignment="center"
                 marginLeft="16" marginRight="16"
                 @tap="closeErrorModal"
                 zIndex="1001">
        <StackLayout class="bg-white rounded-xl py-4 px-4">
          <Label :text="errorModalText"
                 class="text-[#DE6C35] font-inter font-semibold text-base text-center"
                 textWrap="true" />
        </StackLayout>
      </GridLayout>

    </GridLayout>
  </Page>
</template>

<script lang="ts">
import { defineComponent } from 'nativescript-vue';
import Registration from './Registration.vue';
import Main from './MainPage.vue';
import api from '../../services/api';
import { firebase } from '@nativescript/firebase-core';
import { usersService } from '~/init/services';
import { forceRegisterCurrentToken } from '~/fcm';
import { secureStorage } from '~/init/storage'

export default defineComponent({
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      focusedField: null as string | null,
      showPassword: false,
      isLoading: false,
      errorMessage: '',
      showErrorModal: false,
      errorModalText: '',
      errors: {
        email: '',
        password: ''
      },
      touched: {
        email: false,
        password: false
      }
    };
  },
  computed: {
    isFormValid(): boolean {
      return !this.errors.email && 
             !this.errors.password &&
             this.form.email.trim() !== '' && 
             this.form.password.trim() !== '';
    }
  },
  methods: {
    togglePasswordVisibility(): void {
      this.showPassword = !this.showPassword;
    },

    onEmailChange(): void {
      this.touched.email = true;
      this.validateField('email');
    },

    onPasswordChange(): void {
      this.touched.password = true;
      this.validateField('password');
    },

    onBlur(field: 'email' | 'password'): void {
      this.focusedField = null;
      this.touched[field] = true;
      this.validateField(field);
    },

    validateField(field: 'email' | 'password'): void {
      if (field === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!this.form.email.trim()) {
          this.errors.email = '';
        } else if (!emailRegex.test(this.form.email)) {
          this.errors.email = 'Неверный формат e-mail';
        } else {
          this.errors.email = '';
        }
      } else if (field === 'password') {
        if (!this.form.password.trim()) {
          this.errors.password = 'Поле не должно быть пустым';
        } else {
          this.errors.password = '';
        }
      }
    },

    validateAllFields(): boolean {
      this.touched.email = true;
      this.touched.password = true;
      this.validateField('email');
      this.validateField('password');
      return !this.errors.email && !this.errors.password && 
             this.form.email.trim() !== '' && 
             this.form.password.trim() !== '';
    },

    closeErrorModal(): void {
      this.showErrorModal = false;
      this.errorModalText = '';
    },

    async onLogin(): Promise<void> {
      if (!this.validateAllFields() || this.isLoading) return;

      this.isLoading = true;
      this.errorMessage = '';
      this.showErrorModal = false;

      try {
        console.log('Sending login request...');
        const response = await api.post('/login', {
          login: this.form.email,
          password: this.form.password
        });

        const token = response.access_token;
        console.log('Login successful, token:', token);

        api.setToken(token);

        await forceRegisterCurrentToken();

        const fcmToken = await (firebase() as any).messaging().getToken();
        if (fcmToken) {
          await usersService.registerFcmToken(fcmToken);
          console.log('FCM token registered after login');
        }

        this.$navigateTo(Main, {
          transition: { name: 'slideLeft', duration: 300 },
          clearHistory: true
        });

      } catch (error: any) {
        console.error('Login error:', error);

        if (error.response) {
          if (error.response.status === 401) {
            this.errorModalText = 'Неверный email или пароль';
            this.showErrorModal = true;
          } else {
            this.errorModalText = error.response.data?.msg || 'Ошибка сервера';
            this.showErrorModal = true;
          }
        } else {
          this.errorModalText = 'Нет соединения с сервером. Проверьте, запущен ли сервер.';
          this.showErrorModal = true;
        }
      } finally {
        this.isLoading = false;
      }
    },

    async onForgotPassword(): Promise<void> {
      console.log('Forgot password clicked');
      const { alert } = await import('@nativescript/core');
      alert({
        title: "Восстановление пароля",
        message: "Восстановление пароля будет доступно позже",
        okButtonText: "OK"
      });
    },

    goToRegistration(): void {
      this.$navigateTo(Registration, {
        transition: { name: 'fade', duration: 300 }
      });
    }
  }
});
</script>