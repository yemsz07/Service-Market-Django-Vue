<template>
  <div class="space-y-4">

    <!-- Service Title -->
    <div class="field">
      <label for="title" class="font-bold">Service Title *</label>
      <InputText 
        id="title" 
        v-model="form.title" 
        placeholder="Services Title" 
        class="w-full"
      />
    </div>

    <!-- Description -->
    <div class="field">
      <label for="description" class="font-bold">Description *</label>
      <InputText 
        id="description" 
        v-model="form.description" 
        placeholder="Describe your service..." 
        class="w-full"
      />
    </div>

    <!-- Category -->
    <div class="field">
      <label for="category" class="font-bold">Category *</label>
      <Select 
        id="category" 
        v-model="form.category" 
        :options="props.categories" 
        optionLabel="name" 
        optionValue="id"
        placeholder="Select a Category" 
        class="w-full"
        :loading="props.loading"
      />
    </div>

    <!-- Price -->
    <div class="field">
      <label for="price" class="font-bold">Price (₱) *</label>
      <InputNumber 
        id="price" 
        v-model="form.price" 
        mode="currency" 
        currency="PHP" 
        locale="en-PH" 
        class="w-full"
      />
    </div>

    <!-- City -->
    <div class="field">
      <label for="service_city" class="font-bold">City *</label>
      <InputText 
        id="service_city" 
        v-model="form.service_city" 
        placeholder="Enter your city" 
        class="w-full"
      />
    </div>

    <!-- Image Upload -->
    <div class="field">
      <label class="font-bold">Service Image</label>
      <input 
        type="file" 
        ref="fileInput" 
        accept="image/*" 
        class="hidden" 
        @change="handleFileUpload" 
      />
      <Button 
        type="button" 
        label="Choose File" 
        icon="pi pi-plus" 
        class="p-button-emerald w-full" 
        @click="$refs.fileInput.click()" 
      />
      <small v-if="selectedFile" class="block mt-1 text-gray-600">
        {{ selectedFile.name }}
      </small>
    </div>

    <!-- Buttons Section -->
    <div class="flex justify-content-end gap-2 mt-4">
      <Button 
        type="button" 
        label="Cancel" 
        icon="pi pi-times" 
        class="p-button-text p-button-secondary" 
        @click="$emit('close')" 
      />
      <Button 
        type="button" 
        label="Save Service" 
        icon="pi pi-check" 
        class="p-button-success" 
        :loading="submitting" 
        @click="submitForm" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import api from '../api/api'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'

// Define props
const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['submitted', 'close'])

const submitting = ref(false)
const selectedFile = ref(null)

const form = reactive({
  title: '',
  description: '',
  category: null,
  price: null,
  service_city: ''
})

// ✅ Debug: Watch for category changes
watch(() => props.categories, (newVal) => {
  console.log('🔄 Categories prop changed:', newVal)
  console.log('📊 Categories count:', newVal?.length)
}, { immediate: true, deep: true })

// ✅ Debug: Check on mount
onMounted(() => {
  console.log('🔍 Component mounted. Categories prop:', props.categories)
  console.log('📊 Categories count:', props.categories?.length)
})

// File Handler
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

// Submit Function
const submitForm = async () => {
  if (!form.title || !form.description || !form.category || !form.price || !form.service_city) {
    alert('Please fill in all required fields.')
    return
  }

  submitting.value = true

  try {
    const formData = new FormData()
    formData.append('name', form.title)
    formData.append('description', form.description)
    formData.append('category', form.category)
    formData.append('price', form.price)
    formData.append('service_city', form.service_city)
    
    if (selectedFile.value) {
      formData.append('image', selectedFile.value)
    }

    console.log('Submitting service with data:')
    for (let pair of formData.entries()) {
      console.log(pair[0] + ':', pair[1])
    }

    const response = await api.post('/create-service/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    console.log('Service created successfully:', response.data)
    emit('submitted')

  } catch (error) {
    console.error('Error saving service:', error.response?.data || error)
    const errorMessage = error.response?.data?.category?.[0] || 
                        error.response?.data?.message || 
                        error.response?.data?.error ||
                        'Failed to save service. Please check the console for details.'
    alert(errorMessage)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.hidden {
  display: none;
}
</style>