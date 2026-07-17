
import password from 'primevue/password';

<template>

     <div class="home-page">
        <div class="reg-container">
            <form @submit.prevent="register" class="reg-form">
                <i class="pi pi-user" style="font-size: 2.5rem"></i>
                <input v-model="username" type="text" placeholder="Username" class="input-field" required> 
                <input v-model="password" type="password" placeholder="Password" class="input-field" required>
                <input v-model="email" type="email" placeholder="Email" class="input-field" required>
                <button type="submit" class="button-field">Register</button>
                <router-link to="/reglog">Already have an account? Login</router-link>
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
            alert('Registration successful!')
            router.push('/reglog')

        } catch (err) {

            if (err.response) {
                error.value = err.response.data.detail
            } else {
                error.value = 'Server Error'
            }

        } finally {
            loading.value = false
        }
    }

    </script>

    <style>

    .reg-container {
       display: flex;
    justify-content: center;
    align-items: center;
    height: 50vh;
    border: 2px solid #ccc !important;
    border-radius: 20px !important;
    padding: 0.5rem 0.75rem !important;
    }

    .reg-form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .pi-user {
        text-align: center;
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

    </style>