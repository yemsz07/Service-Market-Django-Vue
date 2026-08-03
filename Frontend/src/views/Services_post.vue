<template>
  <div class="inquiries-portal">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-text">
        <h2>Service Inquiries Portal</h2>
        <p>Manage and respond to client inquiries received from ServicesView.</p>
      </div>
      <div class="header-actions">
        <button class="refresh-btn" @click="fetchInquiries" :disabled="loading">
          <i class="pi pi-refresh" :class="{ 'pi-spin': loading }"></i> Refresh
        </button>

        <!-- 🚀 UPDATED: Pinatatakbo na ang status check function sa halip na direktang buksan ang modal -->
        <button class="create-btn" @click="handleCreateServiceClick" :disabled="checkingStatus">
          <i class="pi" :class="checkingStatus ? 'pi-spin pi-spinner' : 'pi-plus'"></i> Create Service
        </button>

        <!-- 🚀 1. APPLY / PROVIDER VERIFICATION MODAL DIALOG -->
      <Dialog 
        v-model:visible="showCreateModal" 
        header="Create New Service"
        :modal="true"
        :style="{ width: '50vw' }"
      >
        <!-- Pinalitan na ng Child Component! -->
        <CreateServiceForm 
          :categories="categories" 
          @submitted="handleSuccess" 
          @close="showCreateModal = false" 
        />
      </Dialog>

      <Dialog 
        v-model:visible="showApplyModal" 
        header="Apply as Service Provider" 
        :style="{ width: '50vw' }" 
        :breakpoints="{ '960px': '75vw', '641px': '90vw' }" 
        :modal="true" 
        :draggable="false"
        class="p-fluid"
      >
        <ApplyProviderForm @submitted="handleApplicationSubmitted" />
      </Dialog>

      </div>
    </div>
    

    <!-- Summary Stats Bar -->
    <div class="stats-overview">
      <div class="stat-card">
        <span class="stat-label">Total Inquiries</span>
        <span class="stat-value">{{ inquiries.length }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Pending</span>
        <span class="stat-value text-warning">
          {{ inquiries.filter(i => i.status === 'pending').length }}
        </span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Responded</span>
        <span class="stat-value text-success">
          {{ inquiries.filter(i => i.status === 'responded').length }}
        </span>
      </div>
    </div>

    <!-- Main Table Container -->
    <div class="table-card">
      <DataTable 
        :value="inquiries" 
        :loading="loading"
        paginator 
        :rows="10"
        responsiveLayout="scroll"
        selectionMode="single"
        @row-click="onRowClick"
        class="custom-table"
      >
        <!-- Empty State inside Table -->
        <template #empty>
          <div class="empty-table">
            <i class="pi pi-inbox"></i>
            <p>No client inquiries found yet.</p>
          </div>
        </template>

        <!-- Column: Client Name -->
        <Column field="client_name" header="Client Name" sortable>
          <template #body="slotProps">
            <div class="client-info-cell">
              <div class="avatar-sm">
                {{ getInitial(slotProps.data.client_name || slotProps.data.client_email) }}
              </div>
              <div>
                <span class="font-bold block">{{ slotProps.data.client_name || 'Anonymous Client' }}</span>
                <span class="text-xs text-muted">{{ slotProps.data.client_email }}</span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Column: Service Requested -->
        <Column field="service_name" header="Service Inquired" sortable>
          <template #body="slotProps">
            <span class="service-badge">
              <i class="pi pi-briefcase mr-1"></i>
              {{ slotProps.data.service_title || slotProps.data.service_name || 'General Inquiry' }}
            </span>
          </template>
        </Column>

        <!-- Column: Preview Message -->
        <Column header="Message Preview">
          <template #body="slotProps">
            <span class="message-preview">
              {{ truncateText(slotProps.data.message, 45) }}
            </span>
          </template>
        </Column>

        <!-- Column: Date Received -->
        <Column field="created_at" header="Date Received" sortable>
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>

        <!-- Column: Status -->
        <Column field="status" header="Status" sortable>
          <template #body="slotProps">
            <span class="status-pill" :class="slotProps.data.status?.toLowerCase()">
              {{ slotProps.data.status || 'Pending' }}
            </span>
          </template>
        </Column>

        <!-- Column: Action -->
        <Column header="Action">
          <template #body="slotProps">
            <button class="view-btn" @click.stop="openInquiryDetail(slotProps.data)">
              View Details
            </button>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- CLIENT INQUIRY DIALOG BOX -->
    <Dialog 
      v-model:visible="displayDialog" 
      header="Client Inquiry Details" 
      :style="{ width: '42rem' }" 
      modal 
      class="inquiry-dialog"
    >
      <div v-if="selectedInquiry" class="dialog-wrapper">
        
        <!-- Client Profile Header -->
        <div class="dialog-client-header">
          <div class="avatar-lg">
            {{ getInitial(selectedInquiry.client_name || selectedInquiry.client_email) }}
          </div>
          <div class="client-meta">
            <h3>{{ selectedInquiry.client_name || 'Client Inquiry' }}</h3>
            <p><i class="pi pi-envelope"></i> {{ selectedInquiry.client_email }}</p>
            <p v-if="selectedInquiry.client_phone"><i class="pi pi-phone"></i> {{ selectedInquiry.client_phone }}</p>
          </div>
          <div class="status-box">
            <span class="status-pill" :class="selectedInquiry.status?.toLowerCase()">
              {{ selectedInquiry.status || 'Pending' }}
            </span>
          </div>
        </div>

        <!-- Service Inquired Info -->
        <div class="dialog-section gray-bg">
          <div class="info-row">
            <span class="info-label">Inquired Service:</span>
            <span class="info-value font-bold">
              {{ selectedInquiry.service_title || selectedInquiry.service_name || 'N/A' }}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Date Sent:</span>
            <span class="info-value">{{ formatDate(selectedInquiry.created_at) }}</span>
          </div>
        </div>

        <!-- Client Message -->
        <div class="dialog-section">
          <h4>Client Message:</h4>
          <div class="message-content-box">
            <p>{{ selectedInquiry.message || 'No message contents provided.' }}</p>
          </div>
        </div>

        <!-- Quick Reply / Action Footer -->
        <div class="dialog-footer-actions">
          <button class="btn-secondary" @click="displayDialog = false">Close</button>
          <a 
            v-if="selectedInquiry.client_email" 
            :href="`mailto:${selectedInquiry.client_email}?subject=Re: Inquiry for ${selectedInquiry.service_title}`"
            class="btn-primary"
          >
            <i class="pi pi-send mr-1"></i> Reply via Email
          </a>
        </div>

      </div>
    </Dialog>
  </div>
</template>


<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../api/api';

// PrimeVue Components
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import CreateServiceForm from './CreateServiceForm.vue'
import ApplyProviderForm from './ApplyProviderForm.vue'

// --- REACTIVE STATES ---

// Inquiry Data States
const inquiries = ref([]);
const loading = ref(true);
const displayDialog = ref(false);
const selectedInquiry = ref(null);

// Create Service Modal & Form States
const showCreateModal = ref(false); 
const isSubmitting = ref(false);

const serviceForm = reactive({
  title: '',
  description: '',
  category: null,
  price: 150,
  image: null
});

// ✅ CHANGE 1: Make categories an empty array instead of hardcoded dummy data
const categories = ref([]); 

// Provider Status & Apply Modal States
const showApplyModal = ref(false);
const providerStatus = ref(null); 
const checkingStatus = ref(false);

// --- HANDLERS & FUNCTIONS ---

const onFileSelect = (event) => {
  serviceForm.image = event.files[0];
};

const handleSuccess = () => {
  showCreateModal.value = false 
}

// Fetch All Inquiries from Django API
const fetchInquiries = async () => {
  loading.value = true;
  try {
    const response = await api.get('get-inquiries/');
    inquiries.value = response.data;
  } catch (error) {
    console.error('Error fetching client inquiries:', error);
  } finally {
    loading.value = false;
  }
};

// ✅ CHANGE 2: Add this new function to fetch categories from your Admin/Backend
const fetchCategories = async () => {
  try {
    // ⚠️ IMPORTANT: Change this URL to match your actual Django endpoint
    const response = await api.get('/categories/'); 
    categories.value = response.data;
    console.log("✅ Categories loaded from backend:", categories.value);
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};

// Check Provider Status before showing Create Service Modal
const handleCreateServiceClick = async () => {
  checkingStatus.value = true;
  try {
    const response = await api.get('/check-provider-status/');
    const status = response.data.approval_status; 
    providerStatus.value = status;

    if (status === 'APPROVED') {
      showCreateModal.value = true;
    } else {
      showApplyModal.value = true;
    }
  } catch (error) {
    console.error('Error checking status:', error);
    showApplyModal.value = true;
  } finally {
    checkingStatus.value = false;
  }
};

// Callback after submitting provider application form
const handleApplicationSubmitted = () => {
  providerStatus.value = 'PENDING';
  alert('Naisumite na ang iyong application! Hintayin ang rebyu ng Admin.');
  showApplyModal.value = false;
};

// Row Click Handlers
const onRowClick = (event) => {
  openInquiryDetail(event.data);
};

const openInquiryDetail = (inquiryData) => {
  selectedInquiry.value = inquiryData;
  displayDialog.value = true;
};

// Helper Functions
const getInitial = (nameOrEmail) => {
  if (!nameOrEmail) return 'C';
  return nameOrEmail.charAt(0).toUpperCase();
};

const truncateText = (text, maxLength) => {
  if (!text) return 'No message content...';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// ✅ CHANGE 3: Fetch BOTH inquiries AND categories when the page loads
onMounted(async () => {
  await fetchInquiries();
  await fetchCategories();
});
</script>


<style scoped>

/* Ginagawang patayo (column) ang pagsunod-sunod ng buttons */
.header-actions {
  display: flex;
  flex-direction: column; /* Gagawing pabaon/papatong ang layout */
  align-items: flex-end;  /* Nakadikit sa kanang bahagi */
  gap: 8px;              /* Espasyo sa pagitan ng Refresh at Create Service */
}

/* Estilo para sa Create Service Button */
.create-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background-color: #059669; /* Indigo color */
  color: #ffffff;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  width: 100%;            /* Opsyonal: Pantay ang lapad sa refresh button */
  max-width: 150px;
}

.create-btn:hover {
  background-color: #4338ca;
}

/* Dashboard Layout */
.inquiries-portal {
  padding: 2rem;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-text h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
}

.header-text p {
  color: #64748b;
  margin: 0;
  font-size: 0.9rem;
}

.refresh-btn {
  background: #fff;
  border: 1px solid #cbd5e1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #334155;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #f1f5f9;
}

/* Stats Overview Cards */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: #fff;
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #0f172a;
}

.text-warning { color: #d97706; }
.text-success { color: #16a34a; }

/* Table Container */
.table-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.empty-table {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.empty-table i {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

/* Table Cells Customizing */
.client-info-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.text-muted {
  color: #64748b;
}

.service-badge {
  background: #f1f5f9;
  color: #334155;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.message-preview {
  color: #475569;
  font-size: 0.88rem;
}

/* Status Pills */
.status-pill {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-pill.pending { background: #fef3c7; color: #92400e; }
.status-pill.responded { background: #dcfce7; color: #166534; }
.status-pill.closed { background: #f1f5f9; color: #475569; }

.view-btn {
  background: #d88b8b;
  color: #fff;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
}

.view-btn:hover {
  background: #c57676;
}

/* Dialog Box Styles */
.dialog-client-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.avatar-lg {
  width: 54px;
  height: 54px;
  background: #f87171;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.client-meta {
  flex-grow: 1;
}

.client-meta h3 {
  margin: 0 0 0.25rem 0;
  color: #0f172a;
}

.client-meta p {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

.dialog-section {
  padding: 1.25rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.dialog-section.gray-bg {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  border: 1px solid #f1f5f9;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-row:last-child { margin-bottom: 0; }

.info-label { color: #64748b; }
.info-value { color: #1e293b; }

.message-content-box {
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 8px;
  color: #334155;
  line-height: 1.6;
  font-size: 0.95rem;
  margin-top: 0.5rem;
  white-space: pre-line;
}

.dialog-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background: #d88b8b;
  color: #fff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
}

.btn-primary:hover { background: #c57676; }
</style>