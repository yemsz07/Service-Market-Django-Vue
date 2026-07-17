<template>
    <div class="home-page">
        <div class="reglog-container">
            <!-- 1. DITO NATIN NILAGAY ANG <form> AT @submit.prevent -->
            <form @submit.prevent="login" class="reglog-form">
                
                <h1 class="tittle-field">Service<span class="accent-text">Market</span></h1>
                
                <!-- 2. NILAGYAN NATIN NG required PARA HINDI PWEDENG BLANKO -->
                <input v-model="username" type="text" placeholder="Username" class="input-field" required> 
                <input v-model="password" type="password" placeholder="Password" class="input-field" required>
                
                <!-- 3. GINAWANG type="submit" AT TINANGGAL ANG @click -->
                <button type="submit" class="button-field">Login</button>
                
                <router-link to="/register">Don't have an account? Register</router-link>
            
            </form> <!-- ISARA ANG </form> DITO -->
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
axios.defaults.withCredentials = true

const login = async () => {
  loading.value = true
  error.value = ''

  try {
   
    const response = await api.post('/login/', {
      username: username.value,
      password: password.value
    })

    console.log("Login Success!", response.data)

    if (globalAuth) {
      globalAuth.authUser.value = response.data.username;
    }

    console.log("Navigating to /home...")
    alert("Login successful!")
    router.push('/home')

  } catch (err) {
    console.error("Login failed:", err)
    
   
    error.value = err.response?.data?.detail || "There's an error to your username and password."
    
  } finally {
    
    loading.value = false 
  }
}
</script>   


<style scoped>
.home-page {
    padding: 2rem;
}


.accent-text {
    color: #d88b8b !important;
}

.tittle-field {
    color: #000000 !important;
}

.button-field {
    background-color: #d88b8b !important;
    color: rgb(255, 255, 255) !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 0.5rem !important;
    cursor: pointer !important;
    &:active {
        background-color: #c07a7a !important;
    }
}

.input-field {
    border: 1px solid #ccc !important;
    border-radius: 5px !important;
    padding: 0.5rem !important;
}

.reglog-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50vh;
    border: 2px solid #ccc !important;
    border-radius: 20px !important;
    padding: 0.5rem 0.75rem !important;
}

.reglog-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

</style>