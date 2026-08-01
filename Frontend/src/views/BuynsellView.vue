<template>
  <div class="home-page">
    <h2>Items Available</h2>

    <div class="grid justify-content-center">

      <!-- Skeleton Loading -->
      <template v-if="isLoading">
        <div v-for="n in 4" :key="n" class="col-12 sm:col-6 md:col-4 lg:col-3 xl:col-3">
          <Card class="shadow-2 border-round-xl h-full">
            <template #header>
              <Skeleton width="100%" height="200px" borderRadius="12px 12px 0 0"></Skeleton>
            </template>
            <template #title>
              <Skeleton width="60%" height="1.5rem" class="mb-2"></Skeleton>
            </template>
            <template #content>
              <Skeleton width="100%" height="3rem"></Skeleton>
            </template>
          </Card>
        </div>
      </template>

      <!-- Real Products Grid -->
      <template v-else>
        <div
          v-for="product in products" 
          :key="product.id"
          class="col-12 sm:col-6 md:col-4 lg:col-3 xl:col-3 mb-4"
        >
          <Card class="product-card shadow-1 border-round-xl overflow-hidden h-full hover:shadow-4 transition-duration-300">
            
            <template #header>
              <!-- 1. Seller Info Header (Parang sa Carousell!) -->
              <div class="seller-header px-3 pt-3 pb-2 flex align-items-center gap-2">
                <img 
                  :src="product.seller?.avatar || 'https://placehold.co/32x32?text=U'" 
                  class="seller-avatar" 
                  alt="avatar" 
                />
                <div class="seller-meta flex flex-column">
                  <span class="seller-name">{{ product.seller?.username || 'ServiceMarket User' }}</span>
                  <span class="seller-time">Kani-kanina lang</span>
                </div>
              </div>

              <!-- 2. Product Image na may saktong Aspect Ratio -->
              <div class="img-wrapper">
                <img :alt="product.name" :src="getProductImage(product)" class="product-img" />
              </div>
            </template>

            <!-- 3. Title -->
            <template #title>
              <h3 class="name-limit mb-0">{{ product.name }}</h3>
            </template>

            <!-- 4. Description -->
            <template #content>
              <p class="desc-limit">{{ product.description }}</p>
            </template>

            <!-- 5. Footer (Price + Wishlist Heart Icon) -->
            <template #footer>
              <div class="flex justify-content-between align-items-center pt-1">
                <div class="price">₱{{ Number(product.price).toLocaleString() }}</div>
                <i class="pi pi-heart text-xl text-500 cursor-pointer hover:text-red-500 transition-colors"></i>
              </div>
            </template>

          </Card>
        </div>
      </template>
      
    </div> 
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Skeleton from 'primevue/skeleton';
import api from '../api/api';

const products = ref([]);
const isLoading = ref(true);

function getProductImage(product) {
  const images = product.images || [];
  if (images.length === 0) return 'https://placehold.co/400x300?text=No+Image';

  const selected = images.find(img => img.is_feature === true) || images[0];
  const baseUrl = api.defaults.baseURL.replace('/api', ''); 
  
  if (selected.image.startsWith('http')) return selected.image;
  return `${baseUrl}${selected.image}`;
}

const fetchService = async () => {
    try {
        const response = await api.get('/buyandsell/');
        products.value = response.data;
        isLoading.value = false;
    } 
    catch (error) {
        console.error('Error:', error); 
        isLoading.value = false; 
    }
};

onMounted(fetchService);
</script>

<style scoped>
.home-page { padding: 2rem; max-width: 1200px; margin: auto; }

/* Styling para sa Seller Header */
.seller-header {
  background-color: #fff;
}
.seller-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}
.seller-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
}
.seller-time {
  font-size: 0.7rem;
  color: #777;
}

/* Image Container Wrapper */
.img-wrapper { 
  height: 190px; 
  overflow: hidden; 
  background-color: #f8f9fa;
}
.product-img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; /* Para hindi ma-stretching ang mukha o larawan */
}

/* Typography styles */
.name-limit { 
  font-size: 1rem; 
  font-weight: 600; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}

.desc-limit { 
  height: 2.2em; 
  overflow: hidden; 
  font-size: 0.8rem; 
  color: #666; 
  line-height: 1.1;
  margin: 0;
}

.price { 
  font-weight: 700; 
  color: #dc2626; 
  font-size: 1.1rem; 
}

/* PrimeVue Card overrides para lumitaw nang malinis */
:deep(.p-card) {
  border: 1px solid #eaeaea;
  border-radius: 12px;
}
:deep(.p-card .p-card-body) {
  padding: 0.8rem 1rem !important; 
}
:deep(.p-card .p-card-content) {
  padding: 0 !important; 
}
:deep(.p-card .p-card-footer) {
  padding: 0.5rem 0 0 0 !important;
}
</style>