<script setup>
import { ref, computed, onBeforeUnmount } from 'vue';
import { saveProduct, deleteProduct } from '../api/apis';

const props = defineProps({
  inventory: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:inventory', 'refresh']);

const activeDragId = ref(null);
const selectedIds = ref([]);

// Helper para sa Image URL
const getProductImageUrl = (product) => {
  console.log("⚡ [VUE AXIOS/STORE] ---- ENTER getProductImageUrl() [Sell_items.vue] ----")
  if (!product) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 No product passed -> returning ''.")
    console.log("⚡ [VUE AXIOS/STORE] ---- EXIT getProductImageUrl() ('') ----")
    return '';
  }
  if (product.imagePreview) {
    console.log(`⚡ [VUE AXIOS/STORE] ✅ Using local imagePreview (blob) for product id=${product.id}`)
    console.log("⚡ [VUE AXIOS/STORE] ---- EXIT getProductImageUrl() (imagePreview) ----")
    return product.imagePreview;
  }

  let imagePath = product.primary_image;
  console.log(`⚡ [VUE AXIOS/STORE] primary_image from backend: ${imagePath}`)
  if (!imagePath && product.images && product.images.length > 0) {
    imagePath = product.images[0].image;
    console.log(`⚡ [VUE AXIOS/STORE] Falling back to images[0].image: ${imagePath}`)
  }
  if (!imagePath) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 No imagePath resolved -> returning ''.")
    console.log("⚡ [VUE AXIOS/STORE] ---- EXIT getProductImageUrl() ('') ----")
    return '';
  }
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    console.log(`⚡ [VUE AXIOS/STORE] ✅ imagePath already absolute: ${imagePath}`)
    console.log("⚡ [VUE AXIOS/STORE] ---- EXIT getProductImageUrl() (absolute) ----")
    return imagePath;
  }

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;

  const finalUrl = `${cleanBase}${cleanPath}`;
  console.log(`⚡ [VUE AXIOS/STORE] ✅ Built final image URL: ${finalUrl}`)
  console.log("⚡ [VUE AXIOS/STORE] ---- EXIT getProductImageUrl() (built url) ----")
  return finalUrl;
};

// ➕ ADD NEW ROW
const addNewRow = () => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER addNewRow() [Sell_items.vue] ====================")
  const newRow = {
    id: 'temp_' + Date.now() + Math.random().toString(36).substr(2, 4),
    name: '',
    description: '',
    price: 0,
    status: 'AVAILABLE', // Default status
    imagePreview: null,
    imageFile: null,
    isEditing: true,
    isNew: true
  };
  console.log(`⚡ [VUE AXIOS/STORE] 🆕 New temp row created -> id: ${newRow.id}`)
  props.inventory.unshift(newRow);
  console.log(`⚡ [VUE AXIOS/STORE] props.inventory count AFTER unshift: ${props.inventory.length}`)
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT addNewRow() ====================")
};

// ✏️ EDIT ROW
const enableEditMode = (rowData) => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER enableEditMode() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] Enabling edit mode for row id: ${rowData.id} | name: ${rowData.name}`)
  rowData.originalData = { ...rowData };
  rowData.isEditing = true;
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT enableEditMode() ====================")
};

// ❌ CANCEL EDIT
const cancelEdit = (rowData) => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER cancelEdit() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] Cancelling edit for row id: ${rowData.id}`)

  if (rowData.originalData) {
    console.log("⚡ [VUE AXIOS/STORE] 🔙 Restoring originalData snapshot.")
    Object.assign(rowData, rowData.originalData);
    delete rowData.originalData;
  }
  
  if (rowData.isNew || String(rowData.id).startsWith('temp_')) { 
    console.log("⚡ [VUE AXIOS/STORE] 🗑️ Row is new/temp -> deleting locally instead of just closing edit mode.")
    deleteRowLocal(rowData.id);
  } else {
    rowData.isEditing = false;
    console.log("⚡ [VUE AXIOS/STORE] ✅ isEditing set to false for existing row.")
  }
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT cancelEdit() ====================")
};

// 💾 SAVE ROW
const saveRow = async (rowData, isBatch = false) => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER saveRow() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] rowData id: ${rowData.id} | isBatch: ${isBatch}`)
  console.log(`⚡ [VUE AXIOS/STORE] rowData snapshot -> name: "${rowData.name}" | price: ${rowData.price} | status: ${rowData.status}`)

  if (!rowData.name || Number(rowData.price) <= 0) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 Validation FAILED -> missing name or invalid price.")
    if (!isBatch) alert('Paki-lagyan ng pangalan at tamang presyo ang produkto.');
    console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT saveRow() (validation fail) ====================")
    return false;
  }
  
  try {
    const formData = new FormData();
    formData.append('name', rowData.name);
    formData.append('description', rowData.description || '');
    formData.append('price', rowData.price);
    formData.append('status', rowData.status || 'AVAILABLE');

    if (rowData.imageFile) {
      formData.append('image', rowData.imageFile);
      console.log(`⚡ [VUE AXIOS/STORE] 🖼️ Attaching imageFile -> name: ${rowData.imageFile.name} | size: ${rowData.imageFile.size} bytes`)
    } else {
      console.log("⚡ [VUE AXIOS/STORE] ⏭️ No imageFile to attach.")
    }

    const targetId = (rowData.isNew || String(rowData.id).startsWith('temp_')) ? null : rowData.id;
    console.log(`⚡ [VUE AXIOS/STORE] Resolved targetId for API call: ${targetId} (null = CREATE, otherwise UPDATE)`)

    console.log("⚡ [VUE AXIOS/STORE] 📤 Calling saveProduct(formData, targetId)...")
    const response = await saveProduct(formData, targetId);
    console.log(`⚡ [VUE AXIOS/STORE] 📦 Response received -> status: ${response?.status} | has data: ${!!response?.data}`)

    if (response && (response.data || response.status === 200 || response.status === 201)) {
      const savedData = response.data || {};
      console.log(`⚡ [VUE AXIOS/STORE] ✅ savedData keys: ${Object.keys(savedData)}`)
      Object.assign(rowData, savedData);
      rowData.isEditing = false;
      rowData.isNew = false;
      rowData.imagePreview = null;
      rowData.imageFile = null;
      console.log(`⚡ [VUE AXIOS/STORE] rowData updated -> id now: ${rowData.id} | isEditing: ${rowData.isEditing}`)

      if (!isBatch) {
        alert('Matagumpay na na-save ang item!');
        emit('refresh');
        console.log("⚡ [VUE AXIOS/STORE] 📡 Emitted 'refresh' event to parent.")
      }
      console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT saveRow() (success -> true) ====================")
      return true;
    }
  } catch (error) {
    console.error('⚡ [VUE AXIOS/STORE] ❌ Error saving item:', error);
    if (!isBatch) alert('Nagka-error sa pag-save ng item.');
    console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT saveRow() (error -> false) ====================")
    return false;
  }
};

// 💾 SAVE ALL EDITED ROWS
const saveAllRows = async () => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER saveAllRows() [Sell_items.vue] ====================")
  const editingRows = props.inventory.filter(item => item.isEditing);
  console.log(`⚡ [VUE AXIOS/STORE] editingRows count: ${editingRows.length}`)

  if (editingRows.length === 0) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 No rows in edit mode -> nothing to save. EXIT.")
    return;
  }

  const invalidItems = editingRows.filter(item => !item.name || Number(item.price) <= 0);
  console.log(`⚡ [VUE AXIOS/STORE] invalidItems count: ${invalidItems.length}`)
  if (invalidItems.length > 0) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 Some items invalid -> aborting batch save.")
    alert('May mga item na walang pangalan o tamang presyo. Paki-ayos muna.');
    console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT saveAllRows() (invalid items) ====================")
    return;
  }

  let successCount = 0;
  for (const item of editingRows) {
    console.log(`⚡ [VUE AXIOS/STORE] 🔁 Batch-saving item id: ${item.id}`)
    const isSuccess = await saveRow(item, true);
    if (isSuccess) successCount++;
  }
  console.log(`⚡ [VUE AXIOS/STORE] Batch save finished -> successCount: ${successCount}/${editingRows.length}`)

  if (successCount > 0) {
    alert(`Matagumpay na na-save ang ${successCount} item(s)!`);
    emit('refresh');
    console.log("⚡ [VUE AXIOS/STORE] 📡 Emitted 'refresh' event to parent after batch save.")
  }
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT saveAllRows() ====================")
};

// 🗑️ SINGLE DELETE ROW
const confirmDelete = async (rowData) => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER confirmDelete() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] Target row id: ${rowData.id} | name: ${rowData.name}`)

  const isConfirmed = confirm(`Sigurado ka bang gusto mong burahin ang "${rowData.name || 'item'}"?`);
  console.log(`⚡ [VUE AXIOS/STORE] User confirmed delete? ${isConfirmed}`)
  if (!isConfirmed) {
    console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT confirmDelete() (cancelled) ====================")
    return;
  }

  try {
    if (rowData.isNew || String(rowData.id).startsWith('temp_')) {
      console.log("⚡ [VUE AXIOS/STORE] 🗑️ Row is local/temp -> deleting locally only (no API call).")
      deleteRowLocal(rowData.id);
    } else {
      console.log(`⚡ [VUE AXIOS/STORE] 📤 Calling deleteProduct(${rowData.id}) API...`)
      await deleteProduct(rowData.id);
      console.log("⚡ [VUE AXIOS/STORE] ✅ API delete successful.")
      deleteRowLocal(rowData.id);
      alert('Matagumpay na nabura ang item.');
      emit('refresh');
      console.log("⚡ [VUE AXIOS/STORE] 📡 Emitted 'refresh' event to parent.")
    }
  } catch (error) {
    console.error('⚡ [VUE AXIOS/STORE] ❌ Error deleting product:', error);
    alert('Nagka-error sa pagbura ng item sa database.');
  }
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT confirmDelete() ====================")
};

// 🗑️ MULTIPLE / BULK DELETE
const deleteSelectedRows = async () => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER deleteSelectedRows() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] selectedIds count: ${selectedIds.value.length} | ids: ${JSON.stringify(selectedIds.value)}`)

  if (selectedIds.value.length === 0) {
    console.log("⚡ [VUE AXIOS/STORE] 🚫 Nothing selected -> EXIT.")
    return;
  }

  const isConfirmed = confirm(`Sigurado ka bang gusto mong burahin ang ${selectedIds.value.length} na napiling item(s)?`);
  console.log(`⚡ [VUE AXIOS/STORE] User confirmed bulk delete? ${isConfirmed}`)
  if (!isConfirmed) {
    console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT deleteSelectedRows() (cancelled) ====================")
    return;
  }

  let deleteCount = 0;
  for (const id of selectedIds.value) {
    try {
      if (String(id).startsWith('temp_')) {
        console.log(`⚡ [VUE AXIOS/STORE] 🗑️ Local delete for temp id: ${id}`)
        deleteRowLocal(id);
        deleteCount++;
      } else {
        console.log(`⚡ [VUE AXIOS/STORE] 📤 API delete for id: ${id}`)
        await deleteProduct(id);
        deleteRowLocal(id);
        deleteCount++;
      }
    } catch (error) {
      console.error(`⚡ [VUE AXIOS/STORE] ❌ Error deleting item ${id}:`, error);
    }
  }
  console.log(`⚡ [VUE AXIOS/STORE] Bulk delete finished -> deleteCount: ${deleteCount}`)

  selectedIds.value = [];
  alert(`Matagumpay na nabura ang ${deleteCount} item(s)!`);
  emit('refresh');
  console.log("⚡ [VUE AXIOS/STORE] 📡 Emitted 'refresh' event to parent after bulk delete.")
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT deleteSelectedRows() ====================")
};

const deleteRowLocal = (id) => {
  console.log("⚡ [VUE AXIOS/STORE] ---- ENTER deleteRowLocal() [Sell_items.vue] ----")
  console.log(`⚡ [VUE AXIOS/STORE] Removing id: ${id} from local inventory (before count: ${props.inventory.length})`)
  const updatedInventory = props.inventory.filter(item => item.id !== id);
  console.log(`⚡ [VUE AXIOS/STORE] updatedInventory count AFTER filter: ${updatedInventory.length}`)
  emit('update:inventory', updatedInventory);
  console.log("⚡ [VUE AXIOS/STORE] 📡 Emitted 'update:inventory' event to parent.")
  console.log("⚡ [VUE AXIOS/STORE] ---- EXIT deleteRowLocal() ----")
};

// CHECKBOX SELECT ALL LOGIC
const isAllSelected = computed(() => {
  const result = props.inventory.length > 0 && selectedIds.value.length === props.inventory.length;
  return result;
});

const toggleSelectAll = (e) => {
  console.log("⚡ [VUE AXIOS/STORE] ==================== ENTER toggleSelectAll() [Sell_items.vue] ====================")
  console.log(`⚡ [VUE AXIOS/STORE] Checkbox checked state: ${e.target.checked}`)
  if (e.target.checked) {
    selectedIds.value = props.inventory.map(item => item.id);
    console.log(`⚡ [VUE AXIOS/STORE] ✅ All selected -> selectedIds count: ${selectedIds.value.length}`)
  } else {
    selectedIds.value = [];
    console.log("⚡ [VUE AXIOS/STORE] 🚫 Deselected all -> selectedIds cleared.")
  }
  console.log("⚡ [VUE AXIOS/STORE] ==================== EXIT toggleSelectAll() ====================")
};

// FILE HANDLING
const handleFile = (file, item) => {
  console.log("⚡ [VUE AXIOS/STORE] ---- ENTER handleFile() [Sell_items.vue] ----")
  console.log(`⚡ [VUE AXIOS/STORE] File received -> name: ${file?.name} | type: ${file?.type} | size: ${file?.size} bytes`)

  if (file && file.type.startsWith('image/')) {
    item.imagePreview = URL.createObjectURL(file);
    item.imageFile = file;
    console.log(`⚡ [VUE AXIOS/STORE] ✅ Valid image -> imagePreview blob URL created for item id: ${item.id}`)
  } else {
    console.log("⚡ [VUE AXIOS/STORE] ❌ Invalid file type -> not an image.")
    alert('Paki-pili lang ng tamang Image file.');
  }
  console.log("⚡ [VUE AXIOS/STORE] ---- EXIT handleFile() ----")
};

const onFileSelect = (event, item) => {
  console.log("⚡ [VUE AXIOS/STORE] ---- ENTER onFileSelect() [Sell_items.vue] ----")
  const file = event.target.files && event.target.files[0];
  console.log(`⚡ [VUE AXIOS/STORE] File selected via input: ${file ? file.name : 'NONE'}`)
  if (file) handleFile(file, item);
  console.log("⚡ [VUE AXIOS/STORE] ---- EXIT onFileSelect() ----")
};

const onDragOver = (event, item) => {
  event.preventDefault();
  activeDragId.value = item.id;
};

const onDragLeave = (event, item) => {
  event.preventDefault();
  if (activeDragId.value === item.id) activeDragId.value = null;
};

const onDrop = (event, item) => {
  console.log("⚡ [VUE AXIOS/STORE] ---- ENTER onDrop() [Sell_items.vue] ----")
  event.preventDefault();
  activeDragId.value = null;
  const file = event.dataTransfer?.files?.[0];
  console.log(`⚡ [VUE AXIOS/STORE] File dropped: ${file ? file.name : 'NONE'}`)
  if (file) handleFile(file, item);
  console.log("⚡ [VUE AXIOS/STORE] ---- EXIT onDrop() ----")
};

onBeforeUnmount(() => {
  console.log("⚡ [VUE AXIOS/STORE] 🧹 [Sell_items.vue] onBeforeUnmount -> cleaning up blob URLs...")
  if (Array.isArray(props.inventory)) {
    let revokedCount = 0;
    props.inventory.forEach(item => {
      if (item.imagePreview && item.imagePreview.startsWith('blob:')) {
        URL.revokeObjectURL(item.imagePreview);
        revokedCount++;
      }
    });
    console.log(`⚡ [VUE AXIOS/STORE] 🧹 Revoked ${revokedCount} blob URL(s).`)
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
      <div style="display: flex; gap: 8px;">
        
        <!-- BULK DELETE BUTTON -->
        <button 
          v-if="selectedIds.length > 0" 
          @click="deleteSelectedRows" 
          type="button" 
          class="btn-delete-selected"
        >
          <i class="pi pi-trash"></i> Delete Selected ({{ selectedIds.length }})
        </button>

        <!-- BATCH SAVE ALL BUTTON -->
        <button 
          v-if="inventory.filter(i => i.isEditing).length > 1" 
          @click="saveAllRows" 
          type="button" 
          class="btn-save-all"
        >
          <i class="pi pi-check"></i> Save All Changes ({{ inventory.filter(i => i.isEditing).length }})
        </button>

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

    <!-- TABLE -->
    <div v-else class="table-container">
      <table class="inventory-table">
        <thead>
          <tr>
            <th style="width: 65px;">IMAGE</th>
            <th style="width: 20%;">PRODUCT NAME</th>
            <th style="width: 25%;">DESCRIPTION</th>
            <th style="width: 15%;">PRICE</th>
            <th style="width: 15%;">STATUS</th>
            <th style="width: 18%; text-align: right;">ACTIONS & SELECT</th>
            <th style="width: 32px; text-align: center;">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="custom-checkbox" title="Select All" />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventory" :key="item.id">
            
            <!-- IMAGE COLUMN -->
            <td style="width: 65px; vertical-align: middle;">
              <label 
                v-if="item.isEditing" 
                class="img-upload-box" 
                :class="{ 'is-dragging': activeDragId === item.id }"
                title="Click or Drag & Drop image here"
                @dragover="e => onDragOver(e, item)"
                @dragleave="e => onDragLeave(e, item)"
                @drop="e => onDrop(e, item)"
              >
                <img 
                  v-if="getProductImageUrl(item)" 
                  :src="getProductImageUrl(item)" 
                  class="img-thumb" 
                />
                <div v-else class="upload-placeholder">
                  <i class="pi pi-cloud-upload"></i>
                  <span>Drop / Click</span>
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

            <!-- STATUS (Dropdown pag edting, Badge pag naka-save) -->
            <td style="vertical-align: middle;">
              <select v-if="item.isEditing" v-model="item.status" class="input-field">
                <option value="AVAILABLE">AVAILABLE</option>
                <option value="SOLD">SOLD</option>
                <option value="RESERVED">RESERVED</option>
              </select>
              <span 
                v-else 
                class="status-badge"
                :class="{
                  'sold': item.status === 'SOLD',
                  'reserved': item.status === 'RESERVED',
                  'available': item.status === 'AVAILABLE' || !item.status
                }"
              >
                {{ item.status || 'AVAILABLE' }}
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

            <!-- ROW CHECKBOX -->
            <td style="width: 32px; text-align: center; vertical-align: middle;">
              <input type="checkbox" :value="item.id" v-model="selectedIds" class="custom-checkbox" />
            </td>

          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<style scoped>
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

.btn-save-all {
  background-color: #0284c7;
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

.btn-save-all:hover {
  background-color: #0369a1;
}

.btn-delete-selected {
  background-color: #e11d48;
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

.btn-delete-selected:hover {
  background-color: #be123c;
}

.custom-checkbox {
  width: 15px;
  height: 15px;
  cursor: pointer;
  accent-color: #059669;
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

.img-upload-box, .img-preview-box {
  width: 50px !important;
  height: 50px !important;
  min-width: 50px !important;
  min-height: 50px !important;
  max-width: 50px !important;
  max-height: 50px !important;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.img-upload-box {
  border: 2px dashed #34d399;
  background-color: #ecfdf5;
  cursor: pointer;
  position: relative;
}

.img-upload-box:hover, .img-upload-box.is-dragging {
  border-color: #059669;
  background-color: #d1fae5;
  transform: scale(1.03);
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
  background-color: #ffffff;
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

/* STATUS BADGES STYLING */
.status-badge {
  display: inline-block;
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 6px;
  text-transform: uppercase;
}

.status-badge.available {
  background-color: #ecfdf5;
  color: #059669;
}

.status-badge.sold {
  background-color: #f1f5f9;
  color: #64748b;
}

.status-badge.reserved {
  background-color: #fff7ed;
  color: #c2410c;
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