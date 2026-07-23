<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';

defineProps({
  services: {
    type: Array,
    default: () => []
  }
});
</script>

<template>
  <div>
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
</template>