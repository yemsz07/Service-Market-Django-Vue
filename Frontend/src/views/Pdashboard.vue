<script setup>
import { ref } from 'vue';
import Button from 'primevue/button';
import Card from 'primevue/card';

const currentTab = ref('services');

const menuItems = [
  { id: 'services', label: 'Services', icon: 'pi pi-layers' },
  { id: 'sell-items', label: 'Sell Items', icon: 'pi pi-shopping-bag' }
];
</script>

<template>
  <!-- Main layout container na may forced flex row para sa Sidebar at Workspace -->
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
    <!-- Gumamit ako ng basic inline style para puwersahing maging vertical block pababa ang takbo ng cards at table -->
    <div style="display: flex !important; flex-direction: column !important; flex-grow: 1 !important; gap: 24px !important; width: 100% !important;">
      
      <!-- ROW NG CARDS: Pinilit maging horizontal row na hiwalay sa ibaba -->
      <div style="display: flex !important; flex-direction: row !important; gap: 24px !important; width: 100% !important;">
        
        <!-- Active Services Card -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between transition-all hover:shadow-md hover:border-slate-300" style="flex: 1 !important;">
          <div class="flex flex-col gap-1">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Active Services</span>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-4xl font-black text-slate-800 tracking-tight leading-none">12</span>
              <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100/50">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                Live
              </span>
            </div>
          </div>
          <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center border border-indigo-100/30 shadow-2xs">
            <i class="pi pi-layers text-xl"></i>
          </div>
        </div>

        <!-- Items For Sale Card -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200/70 shadow-xs flex items-center justify-between transition-all hover:shadow-md hover:border-slate-300" style="flex: 1 !important;">
          <div class="flex flex-col gap-1">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Items For Sale</span>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-4xl font-black text-slate-800 tracking-tight leading-none font-mono">{{  }}</span>
              <span class="inline-flex items-center text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-1 rounded-full border border-slate-200/30">
                In Stock
              </span>
            </div>
          </div>
          <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center border border-emerald-100/30 shadow-2xs">
            <i class="pi pi-shopping-bag text-xl"></i>
          </div>
        </div>

      </div>

      <!-- 3. WORKSPACE VIEW BOX: Naka-isolate sa ilalim ng row ng cards -->
      <div class="bg-white rounded-2xl border border-slate-200/70 shadow-xs overflow-hidden" style="width: 100% !important; display: block !important;">
        
        <!-- SERVICES WORKSPACE VIEW -->
        <div v-if="currentTab === 'services'">
          <!-- Header -->
          <div class="min-h-[110px] p-6 flex flex-row justify-between items-center border-b border-slate-100 bg-gradient-to-b from-slate-50/50 to-white w-full">
            <div>
              <h2 class="text-xl font-bold text-slate-800 tracking-tight">
                Services Management
              </h2>
              <p class="text-xs text-slate-400 mt-1">
                Overview of your current offerings and active market solutions.
              </p>
            </div>
            <div>
              <Button
                label="Create Service"
                icon="pi pi-plus"
                size="small"
                class="!bg-emerald-500 !border-emerald-500 !hover:bg-emerald-600 !text-white !font-semibold !rounded-xl !px-4 !py-2.5 !text-xs border-0"
              />
            </div>
          </div>
          
          <!-- Empty State Area -->
          <div class="p-8 bg-slate-50/20 w-full">
            <div class="border border-dashed border-slate-200/80 bg-white rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-2xs max-w-lg mx-auto my-4">
              <div class="w-14 h-14 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-4 shadow-3xs">
                <i class="pi pi-server text-slate-400 text-xl"></i>
              </div>
              <h4 class="text-base font-bold text-slate-800 tracking-tight">No services active</h4>
              <p class="text-xs text-slate-400 max-w-xs mt-1 leading-relaxed">
                Get started by creating your first digital or physical service module above.
              </p>
            </div>
          </div>
        </div>

        <!-- SELL ITEMS WORKSPACE VIEW -->
        <div v-else-if="currentTab === 'sell-items'">
          <!-- Header -->
          <div class="min-h-[110px] p-6 flex flex-row justify-between items-center border-b border-slate-100 bg-gradient-to-b from-slate-50/50 to-white w-full">
            <div>
              <h2 class="text-xl font-bold text-slate-800 tracking-tight">
                Product Inventory
              </h2>
              <p class="text-xs text-slate-400 mt-1">
                Manage stock levels, physical pricing, and sales tracking.
              </p>
            </div>
            <div>
              <Button
                label="List New Item"
                icon="pi pi-plus"
                size="small"
                class="!bg-emerald-500 !border-emerald-500 !hover:bg-emerald-600 !text-white !font-semibold !rounded-xl !px-4 !py-2.5 !text-xs border-0"
              />
            </div>
          </div>
          
          <!-- Empty State Area -->
          <div class="p-8 bg-slate-50/20 w-full">
            <div class="border border-dashed border-slate-200/80 bg-white rounded-2xl p-10 flex flex-col items-center justify-center text-center shadow-2xs max-w-lg mx-auto my-4">
              <div class="w-14 h-14 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-4 shadow-3xs">
                <i class="pi pi-box text-slate-400 text-xl"></i>
              </div>
              <h4 class="text-base font-bold text-slate-800 tracking-tight">Inventory is empty</h4>
              <p class="text-xs text-slate-400 max-w-xs mt-1 leading-relaxed">
                Add items to your shop catalog to start receiving market orders.
              </p>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>