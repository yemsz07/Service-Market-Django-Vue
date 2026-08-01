<script setup>
import { ref, computed, onMounted } from 'vue';
import { getPortalDashboard } from '../api/apis';

// Child Component Imports
import SellItems from './Sell_items.vue';
import ServicesPost from './Services_post.vue';

// Navigation State
const currentTab = ref('services');
const menuItems = ref([
  { id: 'services', label: 'Service Inquiries', icon: 'pi pi-inbox' },
  { id: 'sell-items', label: 'Sell Items', icon: 'pi pi-shopping-bag' }
]);

// Shared State Data
const inquiries = ref([]); // 👈 Dito na mapupunta ang service inquiries
const inventory = ref([]);
const isLoading = ref(false);

// Computed Counters
const totalInquiriesCount = computed(() => inquiries.value.length); // 👈 Nilagay na natin bilang Inquiries count
const itemsForSaleCount = computed(() => {
  return inventory.value.filter(item => !item.isEditing).length;
});

// Central Dashboard Data Fetcher
const fetchDashboardData = async () => {
  isLoading.value = true;
  try {
    const response = await getPortalDashboard();
    console.log("Portal Dashboard API Data:", response?.data);

    if (response && response.data) {
      if (Array.isArray(response.data)) {
        inventory.value = response.data.map(item => ({
          ...item,
          status: item.status || 'AVAILABLE',
          isEditing: false,
          imagePreview: null
        }));
      } else {
        const rawItems = response.data.products || response.data.inventory || response.data.items || [];
        inventory.value = rawItems.map(item => ({
          ...item,
          status: item.status || 'AVAILABLE',
          isEditing: false,
          imagePreview: null
        }));
        
        // Kukunin ang inquiries mula sa backend response
        inquiries.value = response.data.inquiries || response.data.services || [];
      }
    }
  } catch (error) {
    console.error('Error fetching portal dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<template>
  <div style="display: flex !important; flex-direction: row !important; gap: 32px !important;" class="p-6 max-w-screen-2xl mx-auto bg-slate-50/50 min-h-screen w-full font-sans antialiased text-slate-900">
    
    <!-- 1. SIDEBAR -->
    <aside class="w-64 shrink-0 space-y-3" style="width: 256px !important; flex-shrink: 0 !important;">
      <div class="px-3 text-[11px] font-bold uppercase tracking-widest text-slate-400">
        Management
      </div>
      <nav class="space-y-1">
        <button 
          v-for="item in menuItems" 
          :key="item.id"
          @click="currentTab = item.id"
          type="button"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 cursor-pointer border-0 outline-hidden',
            currentTab === item.id 
              ? 'bg-white text-indigo-600 shadow-sm shadow-slate-200/80 border border-slate-200/50 font-semibold' 
              : 'bg-transparent text-slate-500 hover:bg-slate-100 hover:text-slate-800'
          ]"
        >
          <i :class="[item.icon, 'text-base transition-colors', currentTab === item.id ? 'text-indigo-600' : 'text-slate-400']"></i>
          <span>{{ item.label }}</span>
        </button>
      </nav>
    </aside>

    <!-- 2. MAIN WORKSPACE CONTAINER -->
    <div style="display: flex !important; flex-direction: column !important; flex-grow: 1 !important; gap: 24px !important; width: 100% !important;">
      
      <!-- TOP COUNTER CARDS -->
      <div style="display: flex !important; flex-direction: row !important; gap: 24px !important; width: 100% !important;">
        
        <!-- Service Inquiries Card -->
        <div 
          @click="currentTab = 'services'"
          class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between cursor-pointer hover:border-indigo-300 transition-all" 
          style="flex: 1 !important;"
        >
          <div class="flex flex-col gap-1">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Service Inquiries</span>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-4xl font-black text-slate-800 tracking-tight leading-none">{{ totalInquiriesCount }}</span>
              <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100/50">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span> Active Leads
              </span>
            </div>
          </div>
          <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center border border-indigo-100/30">
            <i class="pi pi-inbox text-xl"></i>
          </div>
        </div>

        <!-- Items For Sale Card -->
        <div 
          @click="currentTab = 'sell-items'"
          class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between cursor-pointer hover:border-emerald-300 transition-all" 
          style="flex: 1 !important;"
        >
          <div class="flex flex-col gap-1">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Items For Sale</span>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-4xl font-black text-slate-800 tracking-tight leading-none font-mono">
                {{ itemsForSaleCount }}
              </span>
              <span class="inline-flex items-center text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-1 rounded-full border border-slate-200/30">
                In Stock
              </span>
            </div>
          </div>
          <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center border border-emerald-100/30">
            <i class="pi pi-shopping-bag text-xl"></i>
          </div>
        </div>

      </div>

      <!-- 3. WORKSPACE CONTAINER -->
      <div class="bg-white rounded-2xl border border-slate-200/70 shadow-xs overflow-hidden" style="width: 100% !important; display: block !important;">
        
        <!-- SERVICES INQUIRIES WORKSPACE -->
        <ServicesPost 
          v-if="currentTab === 'services'" 
          :inquiries="inquiries" 
        />

        <!-- SELL ITEMS WORKSPACE -->
        <SellItems 
          v-else-if="currentTab === 'sell-items'" 
          :inventory="inventory" 
          @update:inventory="inventory = $event"
          @refresh="fetchDashboardData"
        />

      </div>
    </div>
  </div>
</template>        