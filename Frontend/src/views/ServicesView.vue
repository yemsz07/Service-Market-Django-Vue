<template>
  <div class="services-page">
    <div class="page-header-title">
      <h2>Available Services</h2>
      <p>This is the list of services currently active on your account.</p>
    </div>

    <!-- Loading State -->
    <template v-if="loading">
      <div class="loading-container">
        <p>loading...</p>
      </div>
    </template>

    <!-- Cards Grid -->
    <template v-else-if="services.length > 0">
      <div class="services-grid">
        <div 
          v-for="service in services" 
          :key="service.id" 
          class="service-card" 
        >
          <!-- 📸 TOTOONG IMAGE TAG (May Fallback Icon kung Walang Image) -->
          <div class="card-image-placeholder" @click="openServiceDetail(service)">
            <img 
              v-if="service.image" 
              :src="getImageUrl(service.image)" 
              :alt="service.name"
              class="service-card-img"
              @error="onImageError"
            />
            <i v-else class="pi pi-briefcase" style="font-size: 3rem; color: #d88b8b;"></i>
          </div>

          <!-- Card Content -->
          <div class="card-main-content">
            <h4 class="service-name" @click="openServiceDetail(service)">{{ service.name }}</h4>
            
            <p class="service-provider">
              <i class="pi pi-user" style="font-size: 0.8rem;"></i> 
              Posted by: <strong>{{ service.provider_name || 'Unknown User' }}</strong>
            </p>

            <p class="service-location">{{ service.service_city }}</p>
            
            <div class="service-meta">
              <span class="category-tag">{{ service.category }}</span>
              <span class="status-tag" :class="service.status ? service.status.toLowerCase() : ''">
                {{ service.status }}
              </span>
            </div>

            <!-- Chat Provider Button -->
            <Button 
              :label="!currentUserId ? 'Log in to Chat' : 'Chat Provider'" 
              icon="pi pi-comments" 
              class="p-button-outlined p-button-sm w-full mt-2" 
              :disabled="!currentUserId || !service.provider_user_id || currentUserId === service.provider_user_id"
              @click="!currentUserId ? router.push({ name: 'login' }) : openChat(service.provider_user_id, service.provider_name, service.id, service.name)" 
            />
          </div>

        </div>
      </div>
    </template>

    <!-- Empty State -->
    <template v-else>
      <div class="empty-state">
        <i class="pi pi-inbox" style="font-size: 2rem;"></i>
        <p>No services available.</p>
      </div>
    </template>

    <!-- POPUP/DIALOG CONTAINER -->
    <Dialog 
      v-model:visible="displayServiceDetail" 
      :header="selectedService?.name" 
      :style="{ width: '40rem' }" 
      modal 
      class="custom-dialog"
    >
      <div v-if="selectedService" class="dialog-content">
        
        <!-- Image Preview sa Dialog -->
        <div v-if="selectedService.image" class="dialog-image-container">
          <img :src="getImageUrl(selectedService.image)" :alt="selectedService.name" class="dialog-service-img" />
        </div>

        <div class="dialog-section card-author-header">
          <div class="avatar-circle">
            {{ (selectedService.provider_name || 'U')[0].toUpperCase() }}
          </div>
          <div class="author-details">
            <span class="author-name">{{ selectedService.provider_name || 'ServiceMarket User' }}</span>
            <span class="author-city">Service Provider</span>
          </div>
        </div>

        <div class="dialog-section detail-list">
          <div class="detail-item">
            <span class="label">Location:</span>
            <span class="value">{{ selectedService.service_city }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Category:</span>
            <span class="value">{{ selectedService.category }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Status:</span>
            <span class="status-tag" :class="selectedService.status ? selectedService.status.toLowerCase() : ''">
              {{ selectedService.status }}
            </span>
          </div>
        </div>

        <div class="dialog-section description">
          <h4>Service Description</h4>
          <p>{{ selectedService.description || 'No description provided.' }}</p>
        </div>

        <div class="dialog-section pricing">
          <span class="price-value">₱{{ selectedService.price }}</span>
          <span class="price-type">Per Service / Hour</span>
        </div>

      </div>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import api from '../api/api';

const router = useRouter();

// Data state
const services = ref([]);
const loading = ref(true);
const currentUserId = ref(null);

// Popup state
const displayServiceDetail = ref(false);
const selectedService = ref(null);

const API_BASE_URL = 'http://127.0.0.1:8000'; // Django backend address

// Helper function para sa Image URL handling
const getImageUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  return `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;
};

// Fallback kung sira/broken ang image URL
const onImageError = (event) => {
  event.target.style.display = 'none';
};

// Handler para sa pag-chat sa provider
const openChat = (providerId, providerName, serviceId = null, serviceName = null) => {
  const myId = Number(currentUserId.value);
  const targetProviderId = Number(providerId);

  if (!providerId || myId === targetProviderId) {
    return;
  }

  router.push({
    name: 'messages',
    query: { 
      targetUserId: targetProviderId,
      sellerName: providerName,
      serviceId: serviceId,
      serviceName: serviceName
    }
  });
};

// Fetch Auth Status
const checkAuth = async () => {
  try {
    const response = await api.get('/check-auth/');
    if (response.data && response.data.user) {
      currentUserId.value = response.data.user.id;
    }
  } catch (error) {
    console.warn('User is not authenticated:', error);
    currentUserId.value = null;
  }
};

// Fetch service data from Django API
const fetchService = async () => {
  try {
    const response = await api.get('/services/');
    services.value = response.data || response.data.results || [];
  } catch (error) {
    console.error('Error fetching data:', error);
    services.value = [];
  } finally {
    loading.value = false;
  }
};

// Open dialog handler
const openServiceDetail = (service) => {
  selectedService.value = service;
  displayServiceDetail.value = true;
};

onMounted(async () => {
  await checkAuth();
  await fetchService();
});
</script>

<style scoped>
/* Main Page Container */
.services-page {
  background: #f8fafc;
  padding: 2rem;
  min-height: 100vh;
}

.page-header-title {
  margin-bottom: 2rem;
}

.page-header-title h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.page-header-title p {
  color: #64748b;
  margin: 0;
  font-size: 0.9rem;
}

/* Loading/Empty States */
.loading-container, .empty-state {
  text-align: center;
  color: #64748b;
  padding: 3rem;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Service Card */
.service-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border-color: #d88b8b;
}

/* Image Placeholder */
.card-image-placeholder {
  height: 160px;
  background: #fdf2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f1f5f9;
}

/* Main Content */
.card-main-content {
  padding: 1.25rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.service-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.service-location {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 1rem 0;
}

.service-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  gap: 0.5rem;
}

/* Tags */
.category-tag {
  font-size: 0.7rem;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-weight: 500;
}

.status-tag {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  text-transform: capitalize;
}

.status-tag.active { color: #166534; background: #dcfce7; }
.status-tag.pending { color: #854d0e; background: #fef9c3; }
.status-tag.inactive { color: #991b1b; background: #fee2e2; }

/* Dialog/Popup Styles */
.custom-dialog :deep(.p-dialog-header) {
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
}

.custom-dialog :deep(.p-dialog-title) {
  color: #1e293b;
  font-weight: 700;
}

.dialog-content {
  padding: 1rem 0;
}

.dialog-section {
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.card-author-header {
  padding: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-weight: 600;
  font-size: 1.1rem;
}

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
}

.author-city {
  font-size: 0.8rem;
  color: #64748b;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  gap: 0.75rem;
  font-size: 0.9rem;
}

.detail-item .label {
  font-weight: 600;
  color: #1e293b;
  width: 100px;
}

.detail-item .value {
  color: #64748b;
}

.dialog-section.description h4 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
}

.dialog-section.description p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.dialog-section.pricing {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  color: #d88b8b;
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.price-value {
  font-size: 1.75rem;
  font-weight: 700;
}

.price-type {
  font-size: 0.9rem;
  color: #64748b;
  padding-bottom: 4px;
}

.service-provider {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0.25rem 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Matching Button Color to Logo Palette */
.p-button-outlined {
  color: #c86d64 !important;
  border-color: #c86d64 !important;
}

.p-button-outlined:hover {
  background-color: #c86d64 !important;
  color: #fff !important;
}

.service-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Styling para sa Image sa loob ng Popup Dialog */
.dialog-image-container {
  width: 100%;
  height: 220px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.dialog-service-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

</style>