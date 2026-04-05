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
                class="self-center pt-5 mb-5"
              />
              
              <Label text="Добро пожаловать!" 
                class="text-[#F25C05] font-inter font-bold text-2xl text-center mb-2" />
              
              <StackLayout class="self-center w-full mb-5">
                <Label class="text-[#969696] font-inter font-semibold text-base text-center"
                  text="Заполните данные о себе для создания аккаунта в reCipes"
                  textWrap="true" />
              </StackLayout>
              
              <StackLayout>
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
                    :src="showPassword ? '~/assets/openeyes.png' : '~/assets/closeeyes.png'"
                    :width="showPassword ? 24 : 18" 
                    :height="showPassword ? 16 : 12" 
                    @tap="togglePasswordVisibility('password')" />
                </GridLayout>
                
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
                    :src="showConfirmPassword ? '~/assets/openeyes.png' : '~/assets/closeeyes.png'"
                    :width="showConfirmPassword ? 24 : 18" 
                    :height="showConfirmPassword ? 16 : 12" 
                    @tap="togglePasswordVisibility('confirmPassword')" />
                </GridLayout>
                
                <Button text="Зарегистрироваться"
                  class="rounded-2xl font-inter font-bold text-lg text-white px-4 py-4 mt-4"
                  :class="isFormValid ? 'bg-[#F25C05]' : 'bg-[#969696]'"
                  :isEnabled="isFormValid"
                  textTransform="none"
                  @tap="onRegister"/>
                
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
import Login from './Login.vue';
import Main from './Main.vue';

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
      showConfirmPassword: false,
      isLoading: false
    };
  },
  computed: {
    isFormValid(): boolean {
      return this.form.fullname.trim() !== '' && 
             this.form.email.trim() !== '' && 
             this.form.password.trim() !== '' && 
             this.form.confirmPassword.trim() !== '' &&
             this.form.password === this.form.confirmPassword;
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
      if (!this.isFormValid) return;
      
      this.isLoading = true;
      
      setTimeout(() => {
        this.isLoading = false;
        console.log('Registration successful');
        
        this.$navigateTo(Main, {
          transition: {
            name: 'slideLeft',
            duration: 300
          },
          clearHistory: true
        });
      }, 1000);
    },
    
    goToLogin(): void {
      this.$navigateTo(Login, {
        transition: {
          name: 'fade',
          duration: 300
        }
      });
    }
  }
});
</script>