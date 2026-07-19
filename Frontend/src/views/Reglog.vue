<template>
  <div class="home-page">
    <div class="reglog-container">
      <form @submit.prevent="login" class="reglog-form">
        
        <!-- Brand Header -->
        <div class="brand-header">
          <h1 class="title-field">Service<span class="accent-text">Market</span></h1>
        </div>
        
        <!-- Error Alert Panel -->
        <div v-if="error" class="error-alert">
          {{ error }}
        </div>
        
        <!-- Form Inputs Group -->
        <div class="input-group">
          <label for="username">Username</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="Enter your username" 
            class="input-field" 
            :disabled="loading"
            required 
            autocomplete="username"
          > 
        </div>

        <div class="input-group">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="Enter your password" 
            class="input-field" 
            :disabled="loading"
            required 
            autocomplete="current-password"
          >
        </div>
        
        <!-- Action Button (May Spinner state kapag naglo-loading) -->
        <button type="submit" class="button-field" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Login</span>
        </button>
        
        <!-- Footer Link -->
        <div class="form-footer">
          <router-link to="/register" class="redirect-link">
            Don't have an account? <span class="highlight">Register</span>
          </router-link>
        </div>
    
      </form>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, inject } from 'vue'
import axios from 'axios'
import api from '@/api/api'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const router = useRouter()
const globalAuth = inject('globalAuth')

// Mas magandang global config ito sa main.js, pero pinanatili natin para sa safe credentials
axios.defaults.withCredentials = true

const login = async () => {
  if (loading.value) return; // Iwas double submit kapag may makulit na nag-click

  loading.value = true
  error.value = ''

  try {
    // Dahil HttpOnly cookie ang gamit mo, si Django na ang bahalang mag-drop ng cookie.
    const response = await api.post('/login/', {
      username: username.value,
      password: password.value
    })

    console.log("Login Success!", response.data)

    if (globalAuth) {
      globalAuth.authUser.value = response.data.username;
    }

    // Mas magandang User Experience kung itatapon agad sa home kaysa mag-alert pa
    router.push('/home')

  } catch (err) {
    console.error("Login failed:", err)
    
    // Sinalo natin dito ang error message para lumabas sa template dashboard natin
    error.value = err.response?.data?.detail || "Invalid username or password. Please try again."
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
  min-height: 85vh; /* Tinaasan para maging center talaga sa screen */
  padding: 1.5rem;
  background-color: #f9fafb; /* Malinis na background text para maging lutang ang container */
}

/* Container Glass/Card Design */
.reglog-container {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px; /* Swabe at pabilog na modern standard */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Modern soft shadow */
  padding: 2.5rem 2rem;
}

.reglog-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Typography Aesthetics */
.brand-header {
  text-align: center;
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

/* Error UI Badge */
.error-alert {
  background-color: #fef2f2;
  border: 1px solid #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  text-align: center;
}

/* Input Fields Styling styling */
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
  box-shadow: 0 0 0 3px rgba(216, 139, 139, 0.2); /* Soft focus ring glow */
}

.input-field:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

/* Modern Button and Loaders */
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
  transform: scale(0.98); /* Tactile press micro-interaction */
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

/* Bottom Footer Links */
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