<script setup>
import { ref, onBeforeUnmount } from 'vue';

// 🌐 Standard API Imports
import { saveProduct, deleteProduct } from '../api/apis';

const props = defineProps({
  inventory: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:inventory', 'refresh']);

// Helper para sa Image URL
const getProductImageUrl = (product) => {
  if (!product) return '';
  if (product.imagePreview) return product.imagePreview;

  let imagePath = product.primary_image;
  if (!imagePath && product.images && product.images.length > 0) {
    imagePath = product.images[0].image;
  }
  if (!imagePath) return '';
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) return imagePath;

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;

  return `${cleanBase}${cleanPath}`;
};

// ➕ ADD NEW ROW
const addNewRow = () => {
  props.inventory.unshift({
    id: Date.now(),
    name: '',
    description: '',
    price: 0,
    status: 'AVAILABLE',
    imagePreview: null,
    imageFile: null,
    isEditing: true
  });
};

// ✏️ EDIT ROW
const enableEditMode = (rowData) => {
  rowData.originalData = { ...rowData };
  rowData.isEditing = true;
};

// ❌ CANCEL EDIT
const cancelEdit = (rowData) => {
  if (rowData.originalData) {
    Object.assign(rowData, rowData.originalData);
    delete rowData.originalData;
  }
  
  if (typeof rowData.id === 'number' && rowData.id > 1000000000000) { 
    deleteRowLocal(rowData.id);
  } else {
    rowData.isEditing = false;
  }
};

// 💾 SAVE ROW via Axios
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
    formData.append('status', rowData.status || 'AVAILABLE');

    if (rowData.imageFile) {
      formData.append('image', rowData.imageFile);
    }

    const response = await saveProduct(formData, rowData.id);

    if (response && response.data) {
      Object.assign(rowData, response.data);
      rowData.isEditing = false;
      rowData.imagePreview = null;
      rowData.imageFile = null;
      
      alert('Matagumpay na na-save ang item!');
      emit('refresh');
    }
  } catch (error) {
    console.error('Error saving item:', error);
    alert('Nagka-error sa pag-save ng item.');
  }
};

// 🗑️ DELETE ROW via Axios
const confirmDelete = async (rowData) => {
  const isConfirmed = confirm(`Sigurado ka bang gusto mong burahin ang "${rowData.name || 'item'}"?`);
  if (!isConfirmed) return;

  try {
    if (typeof rowData.id === 'number' && rowData.id > 1000000000000) {
      deleteRowLocal(rowData.id);
    } else {
      await deleteProduct(rowData.id);
      deleteRowLocal(rowData.id);
      alert('Matagumpay na nabura ang item.');
      emit('refresh');
    }
  } catch (error) {
    console.error('Error deleting product:', error);
    alert('Nagka-error sa pagbura ng item sa database.');
  }
};

const deleteRowLocal = (id) => {
  const updatedInventory = props.inventory.filter(item => item.id !== id);
  emit('update:inventory', updatedInventory);
};

// File Select Handler
const onFileSelect = (event, item) => {
  const file = event.target.files && event.target.files[0];
  if (file) {
    item.imagePreview = URL.createObjectURL(file);
    item.imageFile = file;
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
  <div class="custom-inventory-card">
    
    <!-- HEADER SECTION -->
    <div class="card-header">
      <div>
        <h2 class="card-title">Product Inventory</h2>
        <p class="card-subtitle">Manage stock levels, physical pricing, and sales tracking.</p>
      </div>
      <div>
        <button @click="addNewRow" type="button" class="btn-primary">
          <span>+</span> List New Item
        </button>
      </div>
    </div>

    <!-- EMPTY STATE -->
    <div v-if="!inventory || inventory.length === 0" class="empty-box">
      <i class="pi pi-box" style="font-size: 24px; color: #cbd5e1; margin-bottom: 8px;"></i>
      <h4>No items in inventory</h4>
      <p>Click "List New Item" to create your first product.</p>
    </div>

    <!-- STABLE TABLE WITH INLINE SIZING -->
    <div v-else class="table-container">
      <table class="inventory-table">
        <thead>
          <tr>
            <th style="width: 80px;">IMAGE</th>
            <th style="width: 25%;">PRODUCT NAME</th>
            <th style="width: 35%;">DESCRIPTION</th>
            <th style="width: 20%;">PRICE</th>
            <th style="width: 20%; text-align: right;">ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventory" :key="item.id">
            
            <!-- IMAGE COLUMN -->
            <td style="width: 80px; vertical-align: middle;">
              <label 
                v-if="item.isEditing" 
                class="img-upload-box" 
                title="Click to select image"
              >
                <img 
                  v-if="getProductImageUrl(item)" 
                  :src="getProductImageUrl(item)" 
                  class="img-thumb" 
                />
                <div v-else class="upload-placeholder">
                  <i class="pi pi-camera"></i>
                  <span>Upload</span>
                </div>
                <input type="file" accept="image/*" class="hidden-file-input" @change="e => onFileSelect(e, item)" />
              </label>

              <div v-else class="img-preview-box">
                <img 
                  v-if="getProductImageUrl(item)" 
                  :src="getProductImageUrl(item)" 
                  class="img-thumb" 
                />
                <i v-else class="pi pi-image" style="color: #cbd5e1;"></i>
              </div>
            </td>

            <!-- PRODUCT NAME -->
            <td style="vertical-align: middle;">
              <input 
                v-if="item.isEditing" 
                v-model="item.name" 
                type="text" 
                placeholder="Product Name" 
                class="input-field" 
              />
              <span v-else class="text-name">{{ item.name || '-' }}</span>
            </td>

            <!-- DESCRIPTION -->
            <td style="vertical-align: middle;">
              <input 
                v-if="item.isEditing" 
                v-model="item.description" 
                type="text" 
                placeholder="Description" 
                class="input-field" 
              />
              <span v-else class="text-desc">{{ item.description || '-' }}</span>
            </td>

            <!-- PRICE -->
            <td style="vertical-align: middle;">
              <input 
                v-if="item.isEditing" 
                v-model.number="item.price" 
                type="number" 
                step="0.01" 
                class="input-field" 
              />
              <span v-else class="text-price">
                P{{ Number(item.price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
              </span>
            </td>

            <!-- ACTIONS -->
            <td style="vertical-align: middle; text-align: right;">
              <div class="action-btn-group">
                <template v-if="item.isEditing">
                  <button @click="saveRow(item)" type="button" class="btn-save">Save</button>
                  <button @click="cancelEdit(item)" type="button" class="btn-cancel">Cancel</button>
                </template>
                <template v-else>
                  <button @click="enableEditMode(item)" type="button" class="btn-icon" title="Edit Item">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="confirmDelete(item)" type="button" class="btn-icon delete" title="Delete Item">
                    <i class="pi pi-trash"></i>
                  </button>
                </template>
              </div>
            </td>

          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<style scoped>
/* BULLETPROOF SCOPED CSS FOR LAYOUT STABILITY */
.custom-inventory-card {
  width: 100%;
  background-color: #ffffff;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.card-subtitle {
  font-size: 12px;
  color: #94a3b8;
  margin: 4px 0 0 0;
}

.btn-primary {
  background-color: #059669;
  color: #ffffff;
  font-weight: 600;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #047857;
}

.empty-box {
  border: 1px dashed #e2e8f0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  margin: 16px 0;
}

.empty-box h4 {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin: 0;
}

.empty-box p {
  font-size: 11px;
  color: #94a3b8;
  margin: 4px 0 0 0;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  table-layout: fixed;
}

.inventory-table th {
  padding-bottom: 12px;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #e2e8f0;
}

.inventory-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #f1f5f9;
}

/* HARD FIXED IMAGE THUMBNAILS (MAX 56x56) */
.img-upload-box, .img-preview-box {
  width: 56px !important;
  height: 56px !important;
  min-width: 56px !important;
  min-height: 56px !important;
  max-width: 56px !important;
  max-height: 56px !important;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.img-upload-box {
  border: 2px dashed #34d399;
  background-color: #ecfdf5;
  cursor: pointer;
  position: relative;
}

.img-preview-box {
  border: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.img-thumb {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  display: block;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #059669;
  font-size: 8px;
  font-weight: 700;
  text-transform: uppercase;
}

.hidden-file-input {
  display: none !important;
}

.input-field {
  width: 90%;
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  outline: none;
  box-sizing: border-box;
}

.input-field:focus {
  border-color: #10b981;
}

.text-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 12px;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-desc {
  color: #64748b;
  font-size: 12px;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-price {
  font-weight: 700;
  color: #0f172a;
  font-size: 12px;
}

.action-btn-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.btn-save {
  background-color: #059669;
  color: #ffffff;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.btn-cancel {
  background-color: #e2e8f0;
  color: #475569;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.btn-icon {
  background: transparent;
  border: none;
  padding: 6px;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-icon:hover {
  color: #059669;
  background-color: #ecfdf5;
}

.btn-icon.delete:hover {
  color: #e11d48;
  background-color: #ffe4e6;
}
</style>