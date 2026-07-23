<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import { getPortalDashboard, saveProduct } from '../api/apis';

// Navigation / Tabs
const currentTab = ref('services');
const menuItems = ref([
  { id: 'services', label: 'Services', icon: 'pi pi-server' },
  { id: 'sell-items', label: 'Sell Items', icon: 'pi pi-shopping-bag' }
]);

// Data State
const services = ref([]);
const inventory = ref([]);
const isLoading = ref(false);

// Computed Properties
const activeServicesCount = computed(() => services.value.length);
const itemsForSaleCount = computed(() => {
  return inventory.value.filter(item => !item.isEditing).length;
});

// 🟢 Centralized Function para sa Image URL
const getProductImageUrl = (product) => {
  if (!product) return '';

  let imagePath = product.primary_image;

  if (!imagePath && product.images && product.images.length > 0) {
    imagePath = product.images[0].image;
  }

  if (!imagePath) return '';

  // Kung buong URL na mula sa Serializer (https:// o http://)
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  // Siguraduhing tumuturo sa 127.0.0.1:8000 kung saan tumatakbo ang Django
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;

  return `${cleanBase}${cleanPath}`;
};

// 🟢 1. FETCH DASHBOARD DATA FUNCTION (Inayos ang nawawalang function)
const fetchDashboardData = async () => {
  isLoading.value = true;
  try {
    const response = await getPortalDashboard();
    
    if (response && response.data) {
      // Kung ang API response ay listahan ng products
      if (Array.isArray(response.data)) {
        inventory.value = response.data.map(item => ({
          ...item,
          isEditing: false,
          imagePreview: null
        }));
      } else {
        // Kung naka-hiwalay ang structure (e.g. { products: [], services: [] })
        inventory.value = (response.data.products || []).map(item => ({
          ...item,
          isEditing: false,
          imagePreview: null
        }));
        services.value = response.data.services || [];
      }
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
};

// Action Functions
const addNewRow = () => {
  inventory.value.unshift({
    id: Date.now(), // Temporary unique ID
    name: '',
    description: '',
    price: 0,
    imagePreview: null,
    imageFile: null,
    isEditing: true
  });
};

// 🟢 2. SAVE ROW (Inayos ang FormData key name at URL update)
const saveRow = async (rowData) => {
  if (!rowData.name || rowData.price <= 0) {
    alert('Paki-lagyan ng pangalan at tamang presyo ang produkto.');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('name', rowData.name);
    formData.append('description', rowData.description || '');
    formData.append('price', rowData.price);

    // 🟢 DAPAT 'image' ANG KEY NAME, HINDI 'primary_image'
    // Dahil sa Serializer mo: image = serializers.ImageField(write_only=True)
    if (rowData.imageFile) {
      formData.append('image', rowData.imageFile);
    }

    const response = await saveProduct(formData);

    if (response && response.data) {
      // I-update ang row gamit ang permanent details mula sa backend
      Object.assign(rowData, response.data);
      rowData.isEditing = false;
      rowData.imagePreview = null;
      rowData.imageFile = null;
      
      alert('Matagumpay na na-save ang item!');
    }
  } catch (error) {
    console.error('Error saving item:', error);
    alert('Nagka-error sa pag-save ng item. Paki-check ang network tab.');
  }
};

const deleteRow = (id) => {
  inventory.value = inventory.value.filter(item => item.id !== id);
};

const onFileSelect = (event, slotProps) => {
  const file = event.target.files[0];
  if (file) {
    slotProps.data.imagePreview = URL.createObjectURL(file);
    slotProps.data.imageFile = file;
  }
};

const onDragOver = (e) => e.preventDefault();

const onDrop = (e, slotProps) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) {
    slotProps.data.imagePreview = URL.createObjectURL(file);
    slotProps.data.imageFile = file;
  }
};

// Lifecycle Hook
onMounted(() => {
  fetchDashboardData();
});


// 🟢 Safe Error Handler para maiwasan ang Infinite Loop
const handleImageError = (e) => {
  // Prevent infinite looping by checking if we already tried setting a fallback
  if (!e.target.dataset.failed) {
    e.target.dataset.failed = "true";
    
    // Gagamit muna ng inline SVG bilang 100% safe fallback para hindi mag-loop kahit walang assets file
    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%2394a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
  }
};


onBeforeUnmount(() => {
  if (Array.isArray(inventory.value)) {
    inventory.value.forEach(item => {
      if (item.imagePreview && item.imagePreview.startsWith('blob:')) {
        URL.revokeObjectURL(item.imagePreview);
      }
    });
  }
});
</script>

<template>
  <div style="display: flex !important; flex-direction: row !important; gap: 32px !important;" class="p-6 max-w-(screen-2xl) mx-auto bg-slate-50/50 min-h-screen w-full font-sans antialiased text-slate-900">
    
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
      
      <!-- ROW NG CARDS -->
      <div style="display: flex !important; flex-direction: row !important; gap: 24px !important; width: 100% !important;">
        <!-- Active Services -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between" style="flex: 1 !important;">
          <div class="flex flex-col gap-1">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Active Services</span>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-4xl font-black text-slate-800 tracking-tight leading-none">{{ activeServicesCount }}</span>
              <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100/50">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span> Live
              </span>
            </div>
          </div>
          <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center border border-indigo-100/30">
            <i class="pi pi-layers text-xl"></i>
          </div>
        </div>

        <!-- Items For Sale -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between" style="flex: 1 !important;">
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

      <!-- 3. WORKSPACE VIEW BOX -->
      <div class="bg-white rounded-2xl border border-slate-200/70 shadow-xs overflow-hidden" style="width: 100% !important; display: block !important;">
        
        <!-- SERVICES WORKSPACE -->
        <div v-if="currentTab === 'services'">
          <div class="min-h-[110px] p-6 flex flex-row justify-between items-center border-b border-slate-100 bg-gradient-to-b from-slate-50/50 to-white w-full">
            <div>
              <h2 class="text-xl font-bold text-slate-800 tracking-tight">Services Management</h2>
              <p class="text-xs text-slate-400 mt-1">Overview of your current offerings and active market solutions.</p>
            </div>
            <div>
              <Button
                label="Create Service"
                icon="pi pi-plus"
                size="small"
                class="!bg-emerald-500 !border-emerald-500 !hover:bg-emerald-600 !text-white !font-semibold !rounded-xl !px-4 !py-2.5 !text-xs border-0 cursor-pointer"
              />
            </div>
          </div>
          
          <div class="p-6 bg-slate-50/20 w-full">
            <div v-if="services.length === 0" class="border border-dashed border-slate-200/80 bg-white rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-2xs max-w-lg mx-auto my-4">
              <div class="w-14 h-14 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-4 shadow-3xs">
                <i class="pi pi-server text-slate-400 text-xl"></i>
              </div>
              <h4 class="text-base font-bold text-slate-800 tracking-tight">No services active</h4>
              <p class="text-xs text-slate-400 max-w-xs mt-1 leading-relaxed">Get started by creating your first digital or physical service module above.</p>
            </div>

            <div v-else class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-2xs">
              <DataTable :value="services" class="p-datatable-sm text-sm" responsiveLayout="scroll">
                <Column field="name" header="Service Name" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <span class="font-bold text-slate-800 text-sm block">{{ slotProps.data.name }}</span>
                  </template>
                </Column>
                <Column field="description" header="Description" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <span class="text-xs text-slate-400 line-clamp-2 max-w-xs block leading-relaxed">{{ slotProps.data.description || 'No description' }}</span>
                  </template>
                </Column>
                <Column field="price" header="Price" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <span class="font-semibold text-emerald-600 font-mono text-sm block">
                      ₱{{ Number(slotProps.data.price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
                    </span>
                  </template>
                </Column>
                <Column field="service_city" header="Location" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <span class="text-xs text-slate-600 block">{{ slotProps.data.service_city }}</span>
                  </template>
                </Column>
                <Column field="status" header="Status" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-28" bodyClass="p-4 text-center align-middle">
                  <template #body="slotProps">
                    <span :class="[
                      'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border',
                      slotProps.data.status === 'AVAILABLE' 
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-100' 
                        : 'bg-slate-100 text-slate-600 border-slate-200'
                    ]">
                      {{ slotProps.data.status }}
                    </span>
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>

        <!-- SELL ITEMS WORKSPACE -->
        <div v-else-if="currentTab === 'sell-items'">
          <div class="min-h-[110px] p-6 flex flex-row justify-between items-center border-b border-slate-100 bg-gradient-to-b from-slate-50/50 to-white w-full">
            <div>
              <h2 class="text-xl font-bold text-slate-800 tracking-tight">Product Inventory</h2>
              <p class="text-xs text-slate-400 mt-1">Manage stock levels, physical pricing, and sales tracking.</p>
            </div>
            <div>
              <Button
                label="List New Item"
                icon="pi pi-plus"
                size="small"
                @click="addNewRow"
                class="!bg-emerald-500 !border-emerald-500 !hover:bg-emerald-600 !text-white !font-semibold !rounded-xl !px-4 !py-2.5 !text-xs border-0 cursor-pointer"
              />
            </div>
          </div>
          
          <div class="p-6 bg-slate-50/20 w-full">
            <div v-if="inventory.length === 0" class="border border-dashed border-slate-200/80 bg-white rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-2xs max-w-lg mx-auto my-4">
              <div class="w-14 h-14 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-4 shadow-3xs">
                <i class="pi pi-box text-slate-400 text-xl"></i>
              </div>
              <h4 class="text-base font-bold text-slate-800 tracking-tight">Inventory is empty</h4>
              <p class="text-xs text-slate-400 max-w-xs mt-1 leading-relaxed">Add items to your shop catalog to start receiving market orders.</p>
            </div>

            <div v-else class="bg-white border border-slate-200/60 rounded-xl overflow-hidden shadow-2xs">
              <DataTable :value="inventory" class="p-datatable-sm text-sm" :pt="{ tbodyRow: { class: 'h-24' } }" responsiveLayout="scroll">
                
                <!-- 1. IMAGE COLUMN -->
                <Column header="Image" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <!-- EDITING MODE -->
                    <div v-if="slotProps.data.isEditing" 
                         @dragover="onDragOver" 
                         @drop="onDrop($event, slotProps)"
                         style="width: 72px !important; height: 72px !important; min-width: 72px !important; min-height: 72px !important;"
                         class="border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-all cursor-pointer relative overflow-hidden shrink-0 mx-auto"
                    >
                      <div v-if="!slotProps.data.imagePreview" class="text-center p-1 text-[9px] text-slate-400 pointer-events-none">
                        <i class="pi pi-cloud-upload text-sm mb-0.5 text-slate-400"></i>
                        <div>Drop or <span class="text-indigo-500 font-semibold underline">Find</span></div>
                      </div>
                      <img v-else :src="slotProps.data.imagePreview" style="width: 100% !important; height: 100% !important; object-fit: cover !important;" />
                      <input type="file" accept="image/*" @change="onFileSelect($event, slotProps)" class="absolute inset-0 opacity-0 cursor-pointer" />
                    </div>

                    <!-- VIEW MODE -->
                    <div 
                      v-else 
                      style="width: 72px !important; height: 72px !important; min-width: 72px !important; min-height: 72px !important;" 
                      class="rounded-xl overflow-hidden bg-slate-100 flex items-center justify-center border border-slate-200/60 shrink-0 mx-auto"
                    >
                     <img 
                        :src="getProductImageUrl(slotProps.data)" 
                        @error="handleImageError"
                        alt="Product Image"
                        style="width: 100% !important; height: 100% !important; object-fit: cover !important; display: block !important;" 
                      />
                    </div>  
                  </template>
                </Column>

                <!-- 2. PRODUCT NAME COLUMN -->
                <Column header="Product Name" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <InputText v-if="slotProps.data.isEditing" v-model="slotProps.data.name" placeholder="Enter name..." class="w-full p-2 border border-slate-200 rounded-lg text-xs font-sans focus:border-indigo-500 outline-hidden" />
                    <span v-else class="font-bold text-slate-800 text-sm block">{{ slotProps.data.name }}</span>
                  </template>
                </Column>

                <!-- 3. DESCRIPTION COLUMN -->
                <Column header="Description" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <InputText v-if="slotProps.data.isEditing" v-model="slotProps.data.description" placeholder="Short description..." class="w-full p-2 border border-slate-200 rounded-lg text-xs font-sans focus:border-indigo-500 outline-hidden" />
                    <span v-else class="text-xs text-slate-400 line-clamp-2 max-w-xs block leading-relaxed">{{ slotProps.data.description || 'No description' }}</span>
                  </template>
                </Column>

                <!-- 4. PRICE COLUMN -->
                <Column header="Price" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
                  <template #body="slotProps">
                    <InputNumber v-if="slotProps.data.isEditing" v-model="slotProps.data.price" placeholder="0.00" inputClass="w-full p-2 border border-slate-200 rounded-lg text-xs font-mono focus:border-indigo-500 outline-hidden" />
                    <span v-else class="font-semibold text-emerald-600 font-mono text-sm block">
                      ₱{{ Number(slotProps.data.price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
                    </span>
                  </template>
                </Column>

                <!-- 5. ACTIONS COLUMN -->
                <Column header="Actions" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-28" bodyClass="p-4 text-center align-middle">
                  <template #body="slotProps">
                    <div v-if="slotProps.data.isEditing" class="flex gap-2 justify-center items-center">
                      <Button icon="pi pi-check" severity="success" class="p-button-rounded p-button-sm !w-7 !h-7 !p-0 cursor-pointer" @click="saveRow(slotProps.data)" />
                      <Button icon="pi pi-times" severity="danger" class="p-button-rounded p-button-sm p-button-text !w-7 !h-7 !p-0 cursor-pointer" @click="deleteRow(slotProps.data.id)" />
                    </div>
                    
                    <span v-else class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
                      Active
                    </span>
                  </template>
                </Column>

              </DataTable>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
