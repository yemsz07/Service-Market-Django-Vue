<template>
  <div class="marketplace-layout">
    <header class="main-header">
      <div class="header-container">
        
        <!-- Brand Section -->
        <div class="brand-section">
          <div class="logo-box">🛠️</div>
          <h1 class="brand-name">Service<span class="accent-text">Market</span></h1>
          <span class="dev-badge">Beta</span>
        </div>

        <!-- Search Wrapper -->
        <div class="search-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search" 
            class="search-input"
          />
        </div>

        <!-- Actions & Navigation Section -->
        <div class="actions-section">
          <nav class="nav-menu">
            <!-- ALWAYS VISIBLE: Kahit sino pwedeng makakita ng Home -->
            <router-link to="/" class="menu-link" active-class="link-active">
              Home
            </router-link>
            
            <!-- KAPAG HINDI PA NAKALOGIN: Lalabas lang ang Auth button -->
            <template v-if="!isLoggedIn">
              <router-link to="/reglog" class="menu-link auth-btn-solid" active-class="auth-active">
                <i class="pi pi-user mr-2"></i> Register / Login
              </router-link>
            </template>

            <!-- KAPAG NAKALOGIN NA: Lalabas ang mga protected navigation items -->
            <template v-else>
              <router-link to="/services" class="menu-link" active-class="link-active">
                Services
              </router-link>
              <router-link to="/buynsell" class="menu-link" active-class="link-active">
                Buy & Sell
              </router-link>
              <router-link to="/messages" class="menu-link" active-class="link-active">
                Messages
              </router-link>
            </template>
          </nav>

          <div class="vertical-divider"></div>

          <!-- USER CONTROLS: Lalabas lang din ito kung logged in ang user -->
          <div class="user-controls" v-if="isLoggedIn">
            <button class="icon-btn" title="Notifications">
              🔔 <span class="noti-dot"></span>
            </button>
            
            <div class="profile-card">
              <!-- Unang letra ng username para sa avatar -->
              <div class="avatar-circle">{{ userAvatarLetter }}</div>
              
              <div class="profile-info">
                <!-- Tunay na username ng naka-login -->
                <span class="user-name">{{ username }}</span>
                <span class="online-indicator">🟢 Online</span>
              </div>
            </div>

            <!-- AlignJustify / Hamburger Toggle Button -->
            <Button 
              type="button"
              class="menu-toggle-btn" 
              @click="toggleMenu" 
              aria-haspopup="true" 
              aria-controls="overlay_menu"
            >
              <!-- Ligtas at siguradong gumaganang icon mula sa primeicons.css -->
              <i class="pi pi-align-justify" style="font-size: 1.8rem; color: #64748b;"></i>
            </Button>

            <!-- Overlay Menu para sa dropdown -->
            <Menu ref="menu" id="overlay_menu" :model="menuItems" :popup="true" />

            <!-- Logout Button -->
            <button @click="logout" class="menu-link" style="color: #ef4444; border: none; background: transparent; cursor: pointer; margin-left: 10px;">
              Logout
            </button>
          </div>
          
        </div>

      </div>
    </header>

    <main class="content-body">
      <div class="page-container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, provide, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import 'primeicons/primeicons.css'; // Dito nanggagaling ang pi-user at pi-bars
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import api from './api/api';

const router = useRouter();

const authUser = ref(null);
const menu = ref(null); // Ref para sa PrimeVue Menu element

provide('globalAuth', {
  authUser
});

const username = computed(() => authUser.value || 'Guest');
const isLoggedIn = computed(() => authUser.value !== null);

const userAvatarLetter = computed(() => {
  return username.value.charAt(0).toUpperCase();
});

// Toggle para mag-drop down ang menu sa mismong posisyon ng button click
const toggleMenu = (event) => {
  menu.value.toggle(event);
};

// Mga links na bababa pagkinlik ang toggle menu icon
const menuItems = ref([
  {
    label: 'User Portal',
    items: [
      {
        label: 'Portal Dashboard',
        icon: 'pi pi-th-large',
        command: () => {
          router.push('/portal-dashboard'); // Tiyaking tugma ito sa pangalan ng route mo
        }
      },
      {
        label: 'My Account',
        icon: 'pi pi-user',
        command: () => {
          router.push('/settings');
        }
      }
    ]
  }
]);

// Logout handler
const logout = async () => {
  try {
    await api.post('/logout/');
    console.log("Logout successful");
    authUser.value = null;
    router.push('/reglog');
  } catch (err) {
    console.error("Logout failed:", err);
    authUser.value = null;
    router.push('/reglog');
  }
};

onMounted(async () => {
    try {
        const response = await api.get('/check-auth/');

        if (response.data.authenticated) {
            authUser.value = response.data.user.username;
        }
    } catch (err) {
        // User is not authenticated, which is expected
        authUser.value = null;
    }
});



</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Solid Style para sa Auth Button */
.auth-btn-solid {
  background-color: #d88b8b !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  padding: 0.6rem 1.4rem !important;
  border-radius: 20px !important;
  box-shadow: 0 4px 12px rgba(216, 139, 139, 0.25);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease-in-out;
}

.auth-btn-solid:hover {
  background-color: #bf7373 !important;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(216, 139, 139, 0.35);
}

.auth-active {
  background-color: #a85c5c !important;
}

.marketplace-layout {
  font-family: 'Plus Jakarta Sans', sans-serif;
  min-height: 100vh;
  background-color: #f8fafc;
  color: #0f172a;
}

.main-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 76px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}
.logo-box {
  background: linear-gradient(135deg, #d88b8b 0%, #b26b6b 100%);
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.3rem;
  box-shadow: 0 4px 12px rgba(216, 139, 139, 0.2);
}
.brand-name {
  font-size: 1.4rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 0;
  color: #1e293b;
}
.accent-text {
  color: #d88b8b;
}
.dev-badge {
  background-color: #f1f5f9;
  color: #64748b;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  text-transform: uppercase;
}

.search-wrapper {
  position: relative;
  flex-grow: 1;
  max-width: 500px;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.95rem;
  opacity: 0.5;
}
.search-input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: inherit;
  background-color: #f8fafc;
  transition: all 0.2s ease;
}
.search-input:focus {
  outline: none;
  border-color: #d88b8b;
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(216, 139, 139, 0.15);
}

.actions-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-shrink: 0;
}
.nav-menu {
  display: flex;
  gap: 0.5rem;
}
.menu-link {
  text-decoration: none;
  color: #64748b;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  transition: all 0.2s ease;
}
.menu-link:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}
.link-active {
  color: #d88b8b !important;
  background-color: rgba(216, 139, 139, 0.1);
}

.vertical-divider {
  width: 1px;
  height: 24px;
  background-color: #e2e8f0;
}

.user-controls {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.icon-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  position: relative;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
}
.icon-btn:hover {
  background-color: #f1f5f9;
}
.noti-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  border: 2px solid #ffffff;
}
.profile-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.avatar-circle {
  width: 38px;
  height: 38px;
  background-color: #1e293b;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 700;
  font-size: 0.95rem;
}
.profile-info {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  line-height: 1.2;
}
.online-indicator {
  font-size: 0.75rem;
  color: #16a34a;
  font-weight: 500;
}

.content-body {
  padding: 2.5rem 0;
}
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.menu-toggle-btn {
  background: none !important;
  border: none !important;
  padding: 8px !important;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px !important;
  transition: background-color 0.2s ease;
}

.menu-toggle-btn:hover {
  background-color: #f1f5f9 !important;
}
</style>