<script setup>
import { ref, onBeforeUnmount } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import { saveProduct } from '../api/apis';

// Props mula sa Pdashboard (inventory array)
const props = defineProps({
  inventory: {
    type: Array,
    default: () => []
  }
});

// Emits para maipasa ang update sa Parent (Pdashboard) kung kinakailangan
const emit = defineEmits(['update:inventory', 'refresh']);

// Centralized Function para sa Image URL
const getProductImageUrl = (product) => {
  if (!product) return '';

  let imagePath = product.primary_image;

  if (!imagePath && product.images && product.images.length > 0) {
    imagePath = product.images[0].image;
  }

  if (!imagePath) return '';

  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;

  return `${cleanBase}${cleanPath}`;
};

// Actions
const addNewRow = () => {
  props.inventory.unshift({
    id: Date.now(),
    name: '',
    description: '',
    price: 0,
    imagePreview: null,
    imageFile: null,
    isEditing: true
  });
};

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

    if (rowData.imageFile) {
      formData.append('image', rowData.imageFile);
    }

    const response = await saveProduct(formData);

    if (response && response.data) {
      Object.assign(rowData, response.data);
      rowData.isEditing = false;
      rowData.imagePreview = null;
      rowData.imageFile = null;
      
      alert('Matagumpay na na-save ang item!');
      emit('refresh'); // Sabihan ang parent na mag-fetch uli kung kinakailangan
    }
  } catch (error) {
    console.error('Error saving item:', error);
    alert('Nagka-error sa pag-save ng item. Paki-check ang network tab.');
  }
};

const deleteRow = (id) => {
  const updatedInventory = props.inventory.filter(item => item.id !== id);
  emit('update:inventory', updatedInventory);
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

const handleImageError = (e) => {
  if (!e.target.dataset.failed) {
    e.target.dataset.failed = "true";
    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%2394a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
  }
};

onBeforeUnmount(() => {
  if (Array.isArray(props.inventory)) {
    props.inventory.forEach(item => {
      if (item.imagePreview && item.imagePreview.startsWith('blob:')) {
        URL.revokeObjectURL(item.imagePreview);
      }
    });
  }
});
</script>

<template>
  <div>
    <!-- HEADER SECTION -->
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
    
    <!-- TABLE CONTENT -->
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
          
          <!-- IMAGE COLUMN -->
          <Column header="Image" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
            <template #body="slotProps">
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

              <div v-else 
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

          <!-- PRODUCT NAME -->
          <Column header="Product Name" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
            <template #body="slotProps">
              <InputText v-if="slotProps.data.isEditing" v-model="slotProps.data.name" placeholder="Enter name..." class="w-full p-2 border border-slate-200 rounded-lg text-xs font-sans focus:border-indigo-500 outline-hidden" />
              <span v-else class="font-bold text-slate-800 text-sm block">{{ slotProps.data.name }}</span>
            </template>
          </Column>

          <!-- DESCRIPTION -->
          <Column header="Description" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase" bodyClass="p-4 align-middle">
            <template #body="slotProps">
              <InputText v-if="slotProps.data.isEditing" v-model="slotProps.data.description" placeholder="Short description..." class="w-full p-2 border border-slate-200 rounded-lg text-xs font-sans focus:border-indigo-500 outline-hidden" />
              <span v-else class="text-xs text-slate-400 line-clamp-2 max-w-xs block leading-relaxed">{{ slotProps.data.description || 'No description' }}</span>
            </template>
          </Column>

          <!-- PRICE -->
          <Column header="Price" headerClass="bg-slate-50 text-slate-600 font-bold p-4 text-xs uppercase w-36" bodyClass="p-4 align-middle">
            <template #body="slotProps">
              <InputNumber v-if="slotProps.data.isEditing" v-model="slotProps.data.price" placeholder="0.00" inputClass="w-full p-2 border border-slate-200 rounded-lg text-xs font-mono focus:border-indigo-500 outline-hidden" />
              <span v-else class="font-semibold text-emerald-600 font-mono text-sm block">
                ₱{{ Number(slotProps.data.price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
              </span>
            </template>
          </Column>

          <!-- ACTIONS -->
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
</template>