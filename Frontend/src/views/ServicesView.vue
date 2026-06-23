<template>
  <div class="home-page">
    <div class="page-header-title">
      <h2>Available Services</h2>
      <p>This is the list of services currently active on your account.</p>
    </div>

    <div class="data-table-container">
      <template v-if="services.length === 0">
        <p>loading...</p>
      </template>

      <template v-else>
        <DataTable 
          :value="services" 
          paginator 
          :rows="5" 
          :rowsPerPageOptions="[5, 10, 20, 50]" 
          tableStyle="min-width: 50rem"
        >
          <Column field="name" header="Name" style="width: 25%"></Column>
          <Column field="status" header="Status" style="width: 25%"></Column>
          <Column field="service_city" header="City" style="width: 25%"></Column>
          <Column field="category" header="Category" style="width: 25%"></Column>
        </DataTable>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import api from '../api/api';

// Dito ilalagay yung data na kukunin sa Django API
const services = ref([]);

// Ito yung function na kukuha ng data sa Django API
const fetchService = async () => {
  try {
    const response = await api.get('/services/');
    services.value = response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

// Patakbuhin ang pag-fetch pagka-load ng page
onMounted(fetchService);
</script>

<style scoped>
.home-page {
  background: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.page-header-title {
  margin-bottom: 1.5rem;
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

/* Custom border color na terno sa brand theme mo */
.custom-table :deep(.p-datatable-border-color) {
  --p-datatable-border-color: #d88b8b;
}
</style>