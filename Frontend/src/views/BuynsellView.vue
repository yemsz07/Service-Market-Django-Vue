<template>
  <div class="home-page">
    <h2>Items Available </h2>
    
    <Carousel :value="products" :numVisible="5" :responsiveOptions="responsiveOptions">
      <template #item="slotProps">
        
        <div class="card">
          <div class="img-wrapper">
            <img :src="getProductImage(slotProps.data)" class="product-img" />
            <Tag :value="slotProps.data.status" :severity="getSeverity(slotProps.data.status)" class="tag" />
          </div>
          
          <div class="content">
            <h3 class="name">{{ slotProps.data.name }}</h3>
            <p>{{ slotProps.data.description }}</p>
            <p class="city"><i class="pi pi-map-marker"></i> {{ slotProps.data.city }}</p>
            <div class="price">₱{{ Number(slotProps.data.price).toLocaleString() }}</div>
          </div>
        </div>

      </template>
    </Carousel>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Carousel from 'primevue/carousel';
import Tag from 'primevue/tag';

const API_BASE_URL = 'http://127.0.0.1:8000';
const products = ref([]);

// [BINAGO] Inupdate ang responsive settings para sa 5-item view
const responsiveOptions = ref([
    { breakpoint: '1400px', numVisible: 5, numScroll: 1 }, // Default: 5 items
    { breakpoint: '1199px', numVisible: 3, numScroll: 1 }, // Tablet: 3 items
    { breakpoint: '767px',  numVisible: 1, numScroll: 1 }  // Mobile: 1 item
]);

const getProductImage = (product) => {
    const images = product.images || [];
    if (images.length === 0) return 'https://placehold.co/400x300?text=No+Image';
    const selected = images.find(img => img.is_feature === true) || images[0];
    return selected.image.startsWith('http') ? selected.image : `${API_BASE_URL}${selected.image}`;
};

const getSeverity = (status) => {
    const map = { 'AVAILABLE': 'success', 'SOLD': 'danger', 'PENDING': 'warning' };
    return map[status] || 'info';
};

const fetchService = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/buyandsell/`);
        products.value = response.data;
    } catch (error) { console.error('Error:', error); }
};

onMounted(fetchService);
</script>

<style scoped>
.home-page { padding: 2rem; max-width: 1200px; margin: auto; } /* [BINAGO] Inadjust ang max-width para magkasya ang 5 cards */

.card { border: 1px solid #e2e8f0; border-radius: 12px; margin: 0.5rem; overflow: hidden; background: white; }

.img-wrapper { height: 160px; position: relative; overflow: hidden; } /* [BINAGO] Bahagyang binabaan ang height (160px) para hindi masyadong matangkad ang 5 cards */
.product-img { width: 100%; height: 100%; object-fit: cover; }

.content { padding: 0.2rem; } /* [BINAGO] Binawasan ng konti ang padding para hindi magsikip */
.tag { position: absolute; top: 10px; left: 10px; font-size: 0.7rem; } /* [BINAGO] Pinaliit ang tag */
.name { font-size: 0.95rem; margin: 0 0 0.5rem 0; } /* [BINAGO] Pinaliit ang font ng name */
.city { color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem; }
.price { font-weight: bold; color: #dc2626; font-size: 1rem; } /* [BINAGO] Pinaliit ang font ng price */
</style>