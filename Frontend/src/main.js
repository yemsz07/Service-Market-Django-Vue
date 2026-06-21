import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // <--- 1. IMPORT ANG ROUTER MO
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';

const app = createApp(App);

app.use(router); // <--- 2. GAMITIN ANG ROUTER BAGO I-MOUNT

// Isasalpak na natin ang PrimeVue na may temang Aura
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: false,
        }
    }
});

app.mount('#app');