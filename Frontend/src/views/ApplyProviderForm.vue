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
const isLoading = ref(false)

const name = ref('');
const detailedAddress = ref('');
const validIdFile = ref(null);
const providerAvatarFile = ref(null);
const isSubmitting = ref(false);
const errorMessage = ref('');

const submitForm = async () => {
  try {
    isLoading.value = true
    
    // Dito tumatakbo ang Axios POST request mo sa backend
    await axios.post('/provider-applications/create/', {
      // payload data
    })

    // KAPAG SUCCESSFUL ANG API CALL:
    // Sabihan ang Parent Component na natapos na ang submission
    emit('submitted')

  } catch (error) {
    console.error('Error submitting application:', error)
    alert('May nangyaring error sa pag-submit.')
  } finally {
    isLoading.value = false
  }
}

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

  const formData = new FormData();
  formData.append('name', name.value);
  formData.append('detailed_address', detailedAddress.value);
  formData.append('valid_id', validIdFile.value);
  formData.append('provider_avatar', providerAvatarFile.value);

  try {
    const response = await applyAsServices(formData);
    emit('submitted', response.data);
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage.value = error.response.data.error;
    } else if (error.response && error.response.data && error.response.data.detail) {
      errorMessage.value = error.response.data.detail;
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