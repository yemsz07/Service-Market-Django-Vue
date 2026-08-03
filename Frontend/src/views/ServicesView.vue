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
          @click="openServiceDetail(service)"
        >
          <!-- Card Image placeholder -->
          <div class="card-image-placeholder">
            <i class="pi pi-briefcase" style="font-size: 3rem; color: #d88b8b;"></i>
          </div>

                    <!-- Card Content -->
          <div class="card-main-content">
            <h4 class="service-name">{{ service.name }}</h4>
            
            <!-- ✅ BAGONG NILAGAY: Pangalan ng Provider/User -->
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
        
        <div class="dialog-section card-author-header">
          <div class="avatar-circle">U</div>
          <div class="author-details">
            <span class="author-name">{{ selectedService.user_email || 'ServiceMarket User' }}</span>
            <span class="author-city">Member since [Insert Date]</span>
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
          <span class="price-value">₱122</span>
          <span class="price-type">Per Hour</span>
        </div>

      </div>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import api from '../api/api';

// Data state
const services = ref([]);
const loading = ref(true);

// Popup state
const displayServiceDetail = ref(false);
const selectedService = ref(null);

// Fetch service data from Django API
const fetchService = async () => {
  try {
    const response = await api.get('/services/');
    services.value = response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    loading.value = false;
  }
};

// Open dialog handler
const openServiceDetail = (service) => {
  selectedService.value = service;
  displayServiceDetail.value = true;
};

onMounted(fetchService);
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


</style>