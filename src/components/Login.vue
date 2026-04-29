<template>
  <Page actionBarHidden="true" backgroundSpanUnderStatusBar="true" class="bg-[#E9E9ED]">
    <GridLayout rows="*" columns="*">
      <ScrollView row="0" col="0">
        <FlexboxLayout class="flex-col justify-center items-stretch h-full">
          <GridLayout rows="auto" columns="*" class="bg-[#FFFFFF] rounded-2xl mx-4 py-11">
            <StackLayout class="px-4">
              <Image 
                src="~/assets/logoMini.png" 
                width="70" 
                height="70"
                class="self-center pt-4 mb-5"
              />
              
              <Label text="С возвращением!" 
                class="text-[#F25C05] font-inter font-bold text-2xl text-center leading-9 mb-2" />
              
              <StackLayout class="self-center w-full mb-5">
                <Label class="text-[#969696] font-inter font-semibold text-base text-center"
                  text="Войдите в свой аккаунт для работы с reCipes"
                  textWrap="true" />
              </StackLayout>
              
              <Label v-if="errorMessage" 
                :text="errorMessage" 
                class="text-red-500 text-center mb-2 text-sm"
                textWrap="true" />
              
              <StackLayout>
                <GridLayout rows="auto" columns="19, *" 
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
                    autocapitalizationType="none" />
                </GridLayout>

                <GridLayout rows="auto" columns="16, *" 
                  class="bg-[#E9E9ED] rounded-2xl px-4 py-5 mb-4"
                  :class="[
                    'border-5',
                    focusedField === 'password' ? 'border-[#F25C05]' : 'border-[#E9E9ED]'
                  ]">
                  
                  <Image col="0" src="~/assets/key.png" 
                    width="16" height="18" />
                  
                  <TextField col="1" 
                    v-model="form.password"
                    hint="Пароль"
                    class="placeholder-[#969696] bg-transparent text-sm font-inter font-semibold ml-4"
                    :class="form.password ? 'text-[#1E1D2E]' : 'text-[#969696]'"
                    @focus="focusedField = 'password'"
                    @blur="focusedField = null"
                    autocorrect="false"
                    autocapitalizationType="none" />
                </GridLayout>
                
                <Label text="Забыли пароль?" 
                  class="text-[#969696] font-inter font-semibold text-sm text-right mb-4"
                  @tap="onForgotPassword"/>
                
                <Button :text="isLoading ? 'Вход...' : 'Войти'"
                  class="rounded-2xl font-inter font-bold text-lg text-white px-4 py-4 mb-4"
                  :class="isFormValid && !isLoading ? 'bg-[#F25C05]' : 'bg-[#969696]'"
                  :isEnabled="isFormValid && !isLoading"
                  textTransform="none"
                  @tap="onLogin"/>
                
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
import { defineComponent } from 'nativescript-vue';
import Registration from './Registration.vue';
import Main from './Main.vue';
import api from '../../services/api';

export default defineComponent({
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      focusedField: null as string | null,
      isLoading: false,
      errorMessage: ''
    };
  },
  computed: {
    isFormValid(): boolean {
      return this.form.email.trim() !== '' && this.form.password.trim() !== '';
    }
  },
  methods: {
    async onLogin(): Promise<void> {
      if (!this.isFormValid || this.isLoading) return;
      
      this.isLoading = true;
      this.errorMessage = '';
      
      try {
        console.log('Sending login request...');
        const response = await api.post('/users/login', {
          login: this.form.email,
          password: this.form.password
        });
        
        const token = response.access_token;
        console.log('Login successful, token:', token);
        
        api.setToken(token);
        
        this.$navigateTo(Main, {
          transition: { name: 'slideLeft', duration: 300 },
          clearHistory: true
        });
        
      } catch (error: any) {
        console.error('Login error:', error);
        
        if (error.response) {
          if (error.response.status === 401) {
            this.errorMessage = 'Неверный email или пароль';
          } else {
            this.errorMessage = error.response.data?.error || 'Ошибка сервера';
          }
        } else {
          this.errorMessage = 'Нет соединения с сервером. Проверьте, запущен ли сервер.';
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    onForgotPassword(): void {
      console.log('Forgot password clicked');
    },
    
    goToRegistration(): void {
      this.$navigateTo(Registration, {
        transition: { name: 'fade', duration: 300 }
      });
    }
  }
});
</script>