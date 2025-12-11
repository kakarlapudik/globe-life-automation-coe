---
inclusion: manual
---

# Test Data Management Tool - Frontend Standards

This document defines frontend development standards for the Test Data Management Tool using Vue.js, TypeScript, and Vuetify.

## Technology Stack

- Vue 3 with TypeScript and Composition API
- Vite for build tooling
- Vuetify 3 for UI components
- Pinia for state management
- Vue Router for navigation
- VeeValidate for form validation
- Vitest and Vue Test Utils for testing

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable components
│   │   ├── common/         # Generic components
│   │   ├── datasets/       # Dataset-specific components
│   │   ├── schemas/        # Schema-specific components
│   │   └── layouts/        # Layout components
│   ├── views/              # Page/view components
│   ├── composables/        # Composition API composables
│   ├── stores/             # Pinia stores
│   ├── router/             # Vue Router configuration
│   ├── services/           # API service layer
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── plugins/            # Vue plugins (Vuetify, etc.)
│   ├── App.vue
│   └── main.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .eslintrc.js
```

## Component Standards

### Single File Components (SFC)

Always use Vue 3 Composition API with `<script setup>`:

```vue
<script setup lang="ts">
interface Props {
  name: string;
  description: string;
  recordCount: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  select: [id: string];
}>();

const handleSelect = () => {
  emit('select', props.name);
};
</script>

<template>
  <v-card class="pa-4" @click="handleSelect">
    <v-card-title>{{ name }}</v-card-title>
    <v-card-text>{{ description }}</v-card-text>
    <v-card-subtitle>{{ recordCount }} records</v-card-subtitle>
  </v-card>
</template>

<style scoped>
.v-card {
  cursor: pointer;
  transition: all 0.3s;
}
</style>
```

### Component Naming

- Use PascalCase for component names
- Use descriptive names that indicate purpose
- Prefix composables with `use`
- Use `.vue` extension for components

### Props and Types

```typescript
// types/dataset.ts
export interface Dataset {
  id: string;
  name: string;
  description: string;
  schemaId: string;
  environmentId: string;
  recordCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateDatasetRequest {
  name: string;
  description?: string;
  schemaId: string;
  environmentId: string;
}
```

## State Management

### Pinia Stores

```typescript
// stores/datasetStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Dataset } from '@/types/dataset';

export const useDatasetStore = defineStore('dataset', () => {
  // State
  const selectedDataset = ref<Dataset | null>(null);
  const filters = ref({
    search: '',
    environment: '',
  });
  const datasets = ref<Dataset[]>([]);
  const loading = ref(false);

  // Getters
  const filteredDatasets = computed(() => {
    return datasets.value.filter(dataset => {
      const matchesSearch = dataset.name
        .toLowerCase()
        .includes(filters.value.search.toLowerCase());
      const matchesEnv = !filters.value.environment || 
        dataset.environmentId === filters.value.environment;
      return matchesSearch && matchesEnv;
    });
  });

  // Actions
  function setSelectedDataset(dataset: Dataset | null) {
    selectedDataset.value = dataset;
  }

  function updateFilters(newFilters: Partial<typeof filters.value>) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function clearFilters() {
    filters.value = { search: '', environment: '' };
  }

  async function fetchDatasets() {
    loading.value = true;
    try {
      const response = await fetch('/api/v1/datasets');
      datasets.value = await response.json();
    } finally {
      loading.value = false;
    }
  }

  return {
    selectedDataset,
    filters,
    datasets,
    loading,
    filteredDatasets,
    setSelectedDataset,
    updateFilters,
    clearFilters,
    fetchDatasets,
  };
});
```

## Composables

```typescript
// composables/useDatasetFilters.ts
import { computed } from 'vue';
import { useDatasetStore } from '@/stores/datasetStore';

export function useDatasetFilters() {
  const datasetStore = useDatasetStore();

  const filters = computed(() => datasetStore.filters);

  const updateSearch = (search: string) => {
    datasetStore.updateFilters({ search });
  };

  const updateEnvironment = (environment: string) => {
    datasetStore.updateFilters({ environment });
  };

  const clearFilters = () => {
    datasetStore.clearFilters();
  };

  return {
    filters,
    updateSearch,
    updateEnvironment,
    clearFilters,
  };
}
```

## Form Handling

Use VeeValidate for form validation:

```vue
<script setup lang="ts">
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import type { CreateDatasetRequest } from '@/types/dataset';

const schema = yup.object({
  name: yup.string().required('Name is required'),
  description: yup.string(),
  schemaId: yup.string().required('Schema is required'),
  environmentId: yup.string().required('Environment is required'),
});

const { handleSubmit, defineField, errors } = useForm<CreateDatasetRequest>({
  validationSchema: schema,
});

const [name, nameAttrs] = defineField('name');
const [description, descriptionAttrs] = defineField('description');
const [schemaId, schemaIdAttrs] = defineField('schemaId');
const [environmentId, environmentIdAttrs] = defineField('environmentId');

const onSubmit = handleSubmit(async (values) => {
  // Handle form submission
  console.log('Form submitted:', values);
});
</script>

<template>
  <v-form @submit.prevent="onSubmit">
    <v-text-field
      v-model="name"
      v-bind="nameAttrs"
      label="Dataset Name"
      :error-messages="errors.name"
      required
    />
    <v-textarea
      v-model="description"
      v-bind="descriptionAttrs"
      label="Description"
      :error-messages="errors.description"
    />
    <v-btn type="submit" color="primary">
      Create Dataset
    </v-btn>
  </v-form>
</template>
```

## Styling with Vuetify

### Theme Configuration

```typescript
// plugins/vuetify.ts
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976d2',
          secondary: '#dc004e',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
        },
      },
    },
  },
});
```

### Using Scoped Styles

```vue
<template>
  <div class="dataset-container">
    <v-card class="pa-4">
      <!-- Content -->
    </v-card>
  </div>
</template>

<style scoped>
.dataset-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}
</style>
```

## Testing

### Component Testing

```typescript
// components/__tests__/DatasetCard.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createVuetify } from 'vuetify';
import DatasetCard from '../DatasetCard.vue';

const vuetify = createVuetify();

describe('DatasetCard', () => {
  const mockProps = {
    name: 'Test Dataset',
    description: 'Test description',
    recordCount: 1000,
  };

  it('renders dataset information', () => {
    const wrapper = mount(DatasetCard, {
      props: mockProps,
      global: {
        plugins: [vuetify],
      },
    });
    
    expect(wrapper.text()).toContain('Test Dataset');
    expect(wrapper.text()).toContain('Test description');
    expect(wrapper.text()).toContain('1000 records');
  });

  it('emits select event when clicked', async () => {
    const wrapper = mount(DatasetCard, {
      props: mockProps,
      global: {
        plugins: [vuetify],
      },
    });
    
    await wrapper.find('.v-card').trigger('click');
    expect(wrapper.emitted('select')).toBeTruthy();
  });
});
```

## Performance Optimization

- Use `v-once` for static content
- Implement virtual scrolling for large lists (vue-virtual-scroller)
- Lazy load routes and components with `defineAsyncComponent`
- Optimize bundle size with code splitting
- Use `computed` for derived state instead of methods
- Use `shallowRef` and `shallowReactive` when deep reactivity isn't needed

## Accessibility

- Use semantic HTML elements
- Provide ARIA labels where needed
- Ensure keyboard navigation works
- Maintain proper heading hierarchy
- Test with screen readers

## Code Quality

- Run ESLint and fix all warnings
- Use TypeScript strict mode
- Write unit tests for components and composables
- Document complex logic with JSDoc comments
- Follow consistent naming conventions
- Use Vue 3 Composition API consistently

## Package Configuration

```json
{
  "name": "test-data-management-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "vuetify": "^3.4.0",
    "@mdi/font": "^7.3.67",
    "vee-validate": "^4.11.8",
    "yup": "^1.3.3",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.4.0",
    "@vue/test-utils": "^2.4.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "vue-tsc": "^1.8.22",
    "eslint": "^8.53.0",
    "eslint-plugin-vue": "^9.18.1",
    "@typescript-eslint/eslint-plugin": "^6.10.0",
    "@typescript-eslint/parser": "^6.10.0"
  }
}
```

This frontend standards guide ensures consistent, maintainable, and high-quality Vue.js code across the Test Data Management Tool.
