<template>
  <div class="home-page">
    <h2>Items Available</h2>

    <div class="grid justify-content-center">

      <template v-if="isLoading">
        <div v-for="n in 4" :key="n" class="col-12 sm:col-6 md:col-4 lg:col-3 xl:col-3">
          <Card class="shadow-2 border-round-lg h-full">
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

      <template v-else>
        <div
          v-for="product in products" 
          :key="product.id"
          class="col-6 sm:col-6 md:col-4 lg:col-3 xl:col-3"
        >
          <Card class="shadow-2 border-round-lg h-full hover:shadow-6 transition-duration-300">
            <template #header>
              <div class="img-wrapper">
                <img :alt="product.name" :src="getProductImage(product)" class="product-img" />
              </div>
            </template>
            <template #title>
              <h3 class="name-limit">{{ product.name }}</h3>
            </template>
            <template #content>
              <p class="desc-limit">{{ product.description }}</p>
            </template>
            <template #footer>
              <div class="price">₱{{ Number(product.price).toLocaleString() }}</div>
            </template>
          </Card>
        </div>
      </template>
      
    </div> </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card'; // Import nang tama
import Skeleton from 'primevue/skeleton';
import api from '../api/api';

const products = ref([]);



// Sa loob ng iyong component (.vue file)

function getProductImage(product) {
  const images = product.images || [];
  if (images.length === 0) return 'https://placehold.co/400x300?text=No+Image';

  const selected = images.find(img => img.is_feature === true) || images[0];

  // Dito ang magic: kukunin natin ang baseURL mula sa api instance
  const baseUrl = api.defaults.baseURL.replace('/api', ''); 
  
  // Kung nagsisimula sa http, ibig sabihin full URL na ito
  if (selected.image.startsWith('http')) return selected.image;

  // Kung hindi, pagsamahin natin (siguraduhing walang double slash)
  return `${baseUrl}${selected.image}`;
}

const isLoading = ref(true); // Default ay true habang naghihintay ng data

const fetchService = async () => {
    try {
        const response = await api.get('/buyandsell/');
        products.value = response.data;
        isLoading.value = false; // Matapos mag-load, i-set sa false
    } 
    catch (error) {
        console.error('Error:', error); 
        isLoading.value = false; // Even if error, stop loading
    }
};

onMounted(fetchService);
</script>

<style scoped>
.home-page { padding: 2rem; max-width: 1200px; margin: auto; }

/* Mas magandang image container */
.img-wrapper { 
  height: 180px; /* Ginawang 180px para mas compact at kita agad ang content */
  overflow: hidden; 
  border-top-left-radius: 12px; 
  border-top-right-radius: 12px;
}
.product-img { width: 100%; height: 100%; object-fit: cover; }

/* Mas magandang typography */
.name-limit { 
  font-size: 1.05rem; 
  font-weight: 600; 
  margin: 0;
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}

.desc-limit { 
  height: 2.4em; 
  overflow: hidden; 
  font-size: 0.85rem; 
  color: #666; 
  line-height: 1.2;
  margin-top: 0.5rem;
}

.price { 
  font-weight: 700; 
  color: #dc2626; 
  font-size: 1.1rem; 
  margin-top: 0.5rem;
}

/* Tamang padding gamit ang :deep para hindi "dikit" ang text sa gilid */
:deep(.p-card .p-card-body) {
    padding: 1rem !important; 
}
:deep(.p-card .p-card-content) {
    padding: 0 !important; /* Inaalis ang default extra padding sa content */
}
</style>