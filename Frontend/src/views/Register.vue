<template>
  <div class="home-page">
    <div class="reg-container">
      <form @submit.prevent="register" class="reg-form">
        
        <!-- Header Zone with PrimeIcon -->
        <div class="brand-header">
          <div class="icon-wrapper">
            <i class="pi pi-user-plus"></i>
          </div>
          <h1 class="title-field">Create <span class="accent-text">Account</span></h1>
          <p class="subtitle-field">Join the ServiceMarket community today.</p>
        </div>

        <!-- Error Alert Panel -->
        <div v-if="error" class="error-alert">
          {{ error }}
        </div>
        
        <!-- Input Fields -->
        <div class="input-group">
          <label for="username">Username</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="Choose a username" 
            class="input-field" 
            :disabled="loading"
            required
          > 
        </div>

        <div class="input-group">
          <label for="email">Email Address</label>
          <input 
            id="email"
            v-model="email" 
            type="email" 
            placeholder="Enter your email" 
            class="input-field" 
            :disabled="loading"
            required
          >
        </div>

        <div class="input-group">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="Create a strong password" 
            class="input-field" 
            :disabled="loading"
            required
          >
        </div>
        
        <!-- Register Button with Loading Spinner -->
        <button type="submit" class="button-field" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Register</span>
        </button>
        
        <!-- Footer Link -->
        <div class="form-footer">
          <router-link to="/reglog" class="redirect-link">
            Already have an account? <span class="highlight">Login</span>
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import 'primeicons/primeicons.css'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/api'

const router = useRouter()

const username = ref('')
const password = ref('')
const email = ref('')
const loading = ref(false)
const error = ref('')

const register = async () => {
  if (loading.value) return // Iwas double submit

  loading.value = true
  error.value = ''

  if (!username.value.trim() || !password.value.trim() || !email.value.trim()) {
    error.value = 'Please fill in all fields'
    loading.value = false
    return
  }

  try {
    const response = await api.post('/register/', {
      username: username.value,
      password: password.value,
      email: email.value
    })
    
    console.log('Registration successful:', response.data)
    
    // Inalis ang Javascript alert para mas swabe ang transition papuntang login page
    router.push('/reglog')

  } catch (err) {
    if (err.response && err.response.data) {
      // Kung may specific validation errors si Django (e.g., "username already exists")
      const data = err.response.data
      error.value = data.detail || data.username?.[0] || data.email?.[0] || data.password?.[0] || 'Registration failed'
    } else {
      error.value = 'Server Error. Please try again later.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Base Layout Component */
.home-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 85vh; /* Center aligned sa viewport */
  padding: 1.5rem;
  background-color: #f9fafb;
}

/* Container Glass/Card Design */
.reg-container {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px; 
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 2.5rem 2rem;
}

.reg-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header and Icons Aesthetic */
.brand-header {
  text-align: center;
  margin-bottom: 0.25rem;
}

.icon-wrapper {
  color: #d88b8b;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.title-field {
  font-size: 2rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.5px;
}

.accent-text {
  color: #d88b8b;
}

.subtitle-field {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

/* Error Alert UI Box */
.error-alert {
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  text-align: center;
}

/* Input Fields Box Controls */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.input-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
}

.input-field {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.625rem 0.75rem;
  font-size: 0.95rem;
  color: #1f2937;
  transition: all 0.2s ease;
  background-color: #ffffff;
}

.input-field:focus {
  outline: none;
  border-color: #d88b8b;
  box-shadow: 0 0 0 3px rgba(216, 139, 139, 0.2); /* Focus dynamic glow */
}

.input-field:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

/* Modern Button Configurations */
.button-field {
  background-color: #d88b8b;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 0.5rem;
}

.button-field:hover:not(:disabled) {
  background-color: #c57878;
}

.button-field:active:not(:disabled) {
  transform: scale(0.98); /* Micro-interaction bounce */
}

.button-field:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

/* CSS Loading Spinner */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Bottom Nav Links redirect */
.form-footer {
  text-align: center;
  margin-top: 0.5rem;
}

.redirect-link {
  font-size: 0.875rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.2s;
}

.redirect-link .highlight {
  color: #d88b8b;
  font-weight: 600;
}

.redirect-link:hover .highlight {
  text-decoration: underline;
}
</style>