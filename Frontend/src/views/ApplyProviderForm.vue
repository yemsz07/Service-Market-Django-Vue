<template>
  <div class="apply-provider-container">
    <h2>Apply as Service Provider</h2>
    <p class="subtitle">Mag-submit ng verification details para makapag-post ng iyong mga serbisyo.</p>

    <form @submit.prevent="handleSubmit" class="flex flex-column gap-3">
      
      <!-- Error Message Banner -->
      <Message v-if="errorMessage" severity="error" :closable="false">
        {{ errorMessage }}
      </Message>

      <!-- Name of Service Provider -->
      <div class="flex flex-column gap-2">
        <label for="name" class="font-bold">Name of Service Provider</label>
        <InputText 
          id="name" 
          v-model="name" 
          placeholder="Enter your Full Name" 
          class="w-full"
          :disabled="isSubmitting"
        />
      </div>

      <!-- 1. Detailed Address -->
      <div class="flex flex-column gap-2">
        <label for="address" class="font-bold">Detailed Address</label>
        <InputText 
          id="address" 
          v-model="detailedAddress" 
          placeholder="Hal. Block 1 Lot 2, Barangay, Lungsod" 
          class="w-full"
          :disabled="isSubmitting"
        />
      </div>

      <!-- 2. Valid ID Upload -->
      <div class="flex flex-column gap-2">
        <label class="font-bold">Valid ID (Government Issued)</label>
        <input 
          type="file" 
          accept="image/*" 
          class="p-inputtext p-component w-full"
          :disabled="isSubmitting"
          @change="(event) => handleFileChange(event, 'validId')" 
        />
      </div>

      <!-- 3. Provider Avatar Upload -->
      <div class="flex flex-column gap-2">
        <label class="font-bold">Provider Profile Picture (Avatar)</label>
        <input 
          type="file" 
          accept="image/*" 
          class="p-inputtext p-component w-full"
          :disabled="isSubmitting"
          @change="(event) => handleFileChange(event, 'avatar')" 
        />
      </div>

      <!-- 4. Submit Button -->
      <Button 
        type="submit" 
        :label="isSubmitting ? 'Submitting...' : 'Submit Application'" 
        :icon="isSubmitting ? 'pi pi-spin pi-spinner' : 'pi pi-send'"
        :loading="isSubmitting"
        :disabled="isSubmitting"
        class="mt-2"
      />

    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';
import { applyAsServices } from '@/api/apis';

const emit = defineEmits(['submitted']);

const name = ref('');
const detailedAddress = ref('');
const validIdFile = ref(null);
const providerAvatarFile = ref(null);
const isSubmitting = ref(false);
const errorMessage = ref('');

const handleFileChange = (event, fieldName) => {
  const file = event.target.files[0];
  if (!file) return;

  if (fieldName === 'validId') {
    validIdFile.value = file;
  } else if (fieldName === 'avatar') {
    providerAvatarFile.value = file;
  }
};

const handleSubmit = async () => {
  if (!detailedAddress.value.trim() || !validIdFile.value || !providerAvatarFile.value) {
    errorMessage.value = 'Mangyaring kumpletuhin ang lahat ng kailangang fields (Address, Valid ID, at Avatar).';
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';

  // 📄 GUMAGAWA NG MULTIPART FORMDATA PAYLOAD
  const formData = new FormData();
  formData.append('name', name.value);
  formData.append('detailed_address', detailedAddress.value.trim());
  
  // Debug: Log file objects before appending
  console.log('[DEBUG] validIdFile.value:', validIdFile.value);
  console.log('[DEBUG] providerAvatarFile.value:', providerAvatarFile.value);
  console.log('[DEBUG] validIdFile type:', validIdFile.value?.constructor?.name);
  console.log('[DEBUG] providerAvatarFile type:', providerAvatarFile.value?.constructor?.name);
  
  // Siguraduhing totoong File instance ang ina-append
  formData.append('valid_id', validIdFile.value);
  formData.append('provider_avatar', providerAvatarFile.value);

  // Debug: Log FormData contents
  console.log('[DEBUG] FormData entries:');
  for (let [key, value] of formData.entries()) {
    console.log(`  ${key}:`, value, `(type: ${value?.constructor?.name})`);
  }

  try {
    const response = await applyAsServices(formData);
    emit('submitted', response.data);
  } catch (error) {
    console.error('Submission error details:', error.response?.data);
    if (error.response && error.response.data && error.response.data.details) {
      // Kunin ang specific field errors mula sa bagong Django validation response
      const details = error.response.data.details;
      const firstError = Object.values(details)[0];
      errorMessage.value = firstError || 'May validation error sa iyong submission.';
    } else if (error.response && error.response.data && error.response.data.message) {
      // Display user-friendly message for ALREADY_PENDING, ALREADY_APPROVED, etc.
      errorMessage.value = error.response.data.message;
    } else {
      errorMessage.value = 'Nagkaroon ng problema sa pagpapadala ng application. Pakisubukan ulit.';
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.apply-provider-container {
  max-width: 500px;
  margin: 0 auto;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #eaeaea;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
</style>