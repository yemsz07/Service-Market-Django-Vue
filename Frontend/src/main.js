import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// 1. PrimeVue Core
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura'; // Ang bagong standard theme

// 2. Global Styles (Layout at Icons)
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';

const app = createApp(App);

app.use(router);

// 3. PrimeVue Config
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: false,
        }
    }
});

app.mount('#app');