<template>
  <div class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">
        Looking for <span class="highlight-text">Trusted Services</span> or Quality Products?
      </h1>
      <p class="hero-subtitle">
        Find everything you need in one place. From expert helping hands to the best local deals, we've got you covered!
      </p>


      <div class="cta-actions">
        <Button 
          label="Explore Services" 
          icon="pi pi-wrench" 
          size="large" 
          raised 
          class="cta-primary" 
          @click="$router.push('/services')"
        />
        <Button 
          label="Browse Products" 
          icon="pi pi-shopping-bag" 
          size="large" 
          outlined 
          class="cta-secondary" 
          @click="$router.push('/buynsell')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// State para sa search input
const searchQuery = ref('');
</script>

<style scoped>
/* Main Container with subtle grid pattern or clean gradient */
.hero-section {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 5rem 2rem;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02);
  margin-bottom: 2.5rem;
}

.hero-content {
  max-width: 800px;
  width: 100%;
}

/* Typography */
.hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.highlight-text {
  color: #d88b8b; /* Swak sa custom brand theme mo */
}

.hero-subtitle {
  font-size: 1.15rem;
  color: #475569;
  margin-bottom: 2.5rem;
  line-height: 1.6;
}





.text-field {
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}





/* CTA Buttons Placement */
.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-primary {
  background-color: #1e293b !important;
  border-color: #1e293b !important;
  font-weight: 600;
}

.cta-primary:hover {
  background-color: #0f172a !important;
  border-color: #0f172a !important;
}

.cta-secondary {
  color: #475569 !important;
  border-color: #cbd5e1 !important;
  font-weight: 600;
}

.cta-secondary:hover {
  background: #f8fafc !important;
  border-color: #94a3b8 !important;
}

/* Responsive adjustment para sa Mobile view */
@media (max-width: 640px) {
  .hero-title {
    font-size: 2rem;
  }
  .hero-section {
    padding: 3rem 1rem;
  }
  .cta-actions {
    flex-direction: column;
    width: 100%;
  }
  .cta-actions .p-button {
    width: 100%;
  }
}
</style>