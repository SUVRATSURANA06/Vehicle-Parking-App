<template>
  <div class="register-container d-flex flex-column align-items-center justify-content-center">
    <div class="register-box">
      <div class="register-title">User Signup</div>
      <form @submit.prevent="submitRegister">
        <div class="mb-3">
          <label class="register-label">Email ID(Username) :</label>
          <input v-model="form.email" type="email" class="register-input" required placeholder="" />
        </div>
        <div class="mb-3">
          <label class="register-label">Password :</label>
          <input v-model="form.password" type="password" class="register-input" required placeholder="" />
        </div>
        <div class="mb-3">
          <label class="register-label">Fullname :</label>
          <input v-model="form.fullname" type="text" class="register-input" required placeholder="" />
        </div>
        <div class="mb-3">
          <label class="register-label">Address :</label>
          <textarea v-model="form.address" class="register-input" rows="2" required placeholder=""></textarea>
        </div>
        <div class="mb-3">
          <label class="register-label">Pin Code :</label>
          <input v-model="form.pincode" type="text" class="register-input" required placeholder="" />
        </div>
        <button type="submit" class="register-btn" :disabled="loading">Register</button>
      </form>
      <div class="text-center mt-2">
        <a href="#" class="login-here-link" @click.prevent="goToLogin">Login here!</a>
      </div>
      <div v-if="error" class="register-error mt-3">{{ error }}</div>
      <div v-if="success" class="register-success mt-3">{{ success }}</div>
    </div>
    <div class="text-center mt-3" style="font-style: italic; font-size: 1.05rem; color: #222; font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;">No registration required to Admin</div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const form = ref({ email: '', password: '', fullname: '', address: '', pincode: '' })
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const submitRegister = async () => {
      loading.value = true
      error.value = ''
      success.value = ''
      try {
        // Split fullname into first and last name
        let first_name = '', last_name = ''
        if (form.value.fullname) {
          const parts = form.value.fullname.trim().split(' ')
          first_name = parts[0]
          last_name = parts.slice(1).join(' ')
        }
        const payload = {
          email: form.value.email,
          username: form.value.email,
          password: form.value.password,
          first_name,
          last_name,
          address: form.value.address,
          pin_code: form.value.pincode
        }
        const response = await authAPI.register(payload)
        if (response.data.success) {
          success.value = 'Registration successful! Please login.'
          setTimeout(() => router.push('/login'), 1200)
        } else {
          error.value = response.data.message || 'Registration failed.'
        }
      } catch (err) {
        error.value = err.response?.data?.message || 'Registration failed.'
      } finally {
        loading.value = false
      }
    }

    const goToLogin = () => {
      router.push('/login')
    }

    return {
      form,
      loading,
      error,
      success,
      submitRegister,
      goToLogin
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Indie+Flower&display=swap');
html, body {
  width: 100%;
  height: 100vh;
  box-sizing: border-box;
  overflow: hidden;
}
.register-container {
  height: 100vh;
  width: 100%;
  background: none;
  justify-content: center;
  align-items: center;
  display: flex;
  box-sizing: border-box;
}
.register-box {
  border: 2px solid #222;
  border-radius: 32px;
  padding: 24px 24px 16px 24px;
  background: #fff;
  max-width: 420px;
  width: 100%;
  font-family: 'Comic Neue', 'Indie+Flower', cursive, sans-serif;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  margin: 0 auto;
  box-sizing: border-box;
}
@media (max-width: 600px) {
  html, body, .register-container {
    height: auto;
    min-height: 100vh;
    overflow: auto;
  }
  .register-box {
    max-height: none;
  }
}
.register-title {
  color: #7c3aed;
  font-size: 1.6rem;
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  font-weight: bold;
  text-align: center;
  margin-bottom: 18px;
}
.register-label {
  font-family: 'Comic Neue', 'Indie Flower', cursive, sans-serif;
  font-size: 1.1rem;
  color: #222;
  margin-bottom: 4px;
  display: block;
}
.register-input {
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
.register-btn {
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
.register-btn:hover {
  background: #63b3ed;
}
.login-here-link {
  color: #ff9800;
  font-family: inherit;
  font-size: 1.05rem;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}
.login-here-link:hover {
  text-decoration: underline;
}
.register-error {
  color: #e53935;
  font-family: inherit;
  font-size: 1rem;
  text-align: center;
}
.register-success {
  color: #388e3c;
  font-family: inherit;
  font-size: 1rem;
  text-align: center;
}
</style> 