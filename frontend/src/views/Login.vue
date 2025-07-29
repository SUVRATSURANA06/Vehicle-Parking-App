<template>
  <div class="login-container d-flex flex-column align-items-center justify-content-center">
    <div class="login-box">
      <div class="login-title">User Login</div>
      <form @submit.prevent="submitLogin">
        <div class="mb-3">
          <label class="login-label">Registered Email ID:</label>
          <input v-model="form.email" type="email" class="login-input" required placeholder="" />
        </div>
        <div class="mb-3">
          <label class="login-label">Password :</label>
          <input v-model="form.password" type="password" class="login-input" required placeholder="" />
        </div>
        <button type="submit" class="login-btn" :disabled="loading">Login</button>
      </form>
      <div class="text-center mt-2">
        <a href="#" class="create-account-link" @click.prevent="goToRegister">Create Account?</a>
      </div>
      <div v-if="error" class="login-error mt-3">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const form = ref({ email: '', password: '' })
    const loading = ref(false)
    const error = ref('')

    const submitLogin = async () => {
      loading.value = true
      error.value = ''
      try {
        const response = await authAPI.login(form.value)
        if (response.data.success) {
          // Store user data in localStorage
          localStorage.setItem('userData', JSON.stringify(response.data.user))
          if (response.data.is_admin) {
            router.push('/admin/dashboard')
          } else {
            router.push('/user/dashboard')
          }
        } else {
          error.value = response.data.message || 'Login failed.'
        }
      } catch (err) {
        error.value = err.response?.data?.message || 'Login failed.'
      } finally {
        loading.value = false
      }
    }

    const goToRegister = () => {
      router.push('/register')
    }

    return {
      form,
      loading,
      error,
      submitLogin,
      goToRegister
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
.login-container {
  min-height: 80vh;
  width: 100%; /* Changed from 100vw to 100% to prevent horizontal scroll */
  background: none;
  justify-content: center;
  align-items: center;
  display: flex;
}
.login-box {
  border: 2px solid #222;
  border-radius: 32px;
  padding: 36px 36px 24px 36px;
  background: #fff;
  min-width: 320px;
  max-width: 400px;
  width: 100%;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  margin: 0 auto;
}
.login-title {
  color: #7c3aed;
  font-size: 1.6rem;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  font-weight: bold;
  text-align: center;
  margin-bottom: 18px;
}
.login-label {
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  font-size: 1.1rem;
  color: #222;
  margin-bottom: 4px;
  display: block;
}
.login-input {
  width: 100%;
  border: 2px solid #222;
  border-radius: 12px;
  padding: 8px 12px;
  font-size: 1.1rem;
  font-family: inherit;
  margin-bottom: 8px;
  outline: none;
  background: #fff;
}
.login-btn {
  width: 100%;
  background: #90cdf4;
  color: #222;
  border: 2px solid #222;
  border-radius: 8px;
  font-size: 1.1rem;
  font-family: inherit;
  font-weight: bold;
  padding: 6px 0;
  margin-top: 8px;
  transition: background 0.2s;
}
.login-btn:hover {
  background: #63b3ed;
}
.create-account-link {
  color: #ff9800;
  font-family: inherit;
  font-size: 1.05rem;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}
.create-account-link:hover {
  text-decoration: underline;
}
.login-error {
  color: #e53935;
  font-family: inherit;
  font-size: 1rem;
  text-align: center;
}
</style> 