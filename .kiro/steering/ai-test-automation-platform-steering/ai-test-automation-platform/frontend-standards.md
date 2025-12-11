---
inclusion: manual
---

# AI Test Automation Platform - Frontend Standards

## Overview
This document defines the frontend development standards for the AI Test Automation Platform. The platform is built with Vue.js and includes standard test automation UI plus a few additional views for DDFE (Data-Driven Framework Engine) object repository management.

## Technology Stack
- **Vue 3** with TypeScript (Composition API)
- **Tailwind CSS** for styling
- **Pinia** for state management
- **Vue Router** for navigation

## DDFE Object Repository Views

The platform includes three additional views for managing test object repositories:

### 1. Element Repository Browser View
A simple tree/list view showing:
- Applications and pages hierarchy
- UI elements with their selectors
- Search and filter capabilities
- Basic CRUD operations (Create, Read, Update, Delete)

### 2. Element Editor View
A form-based view for editing element definitions:
- Element name and description
- Primary selector (CSS, XPath, ID)
- Fallback selectors
- Element properties (type, visibility, etc.)
- Save/Cancel actions

### 3. Element Usage Analytics View
A dashboard showing:
- Most used elements
- Elements with failures
- Selector health metrics
- Simple charts and statistics

## Component Structure
```
src/components/
├── ddfe/
│   ├── ElementBrowser.vue      # Tree/list view of elements
│   ├── ElementEditor.vue        # Form for editing elements
│   └── ElementAnalytics.vue     # Usage dashboard
└── shared/
    ├── Button.vue
    ├── Input.vue
    └── DataTable.vue
```

## Implementation Guidelines

### Keep It Simple
- Use existing component library where possible
- Minimal custom styling
- Standard CRUD patterns
- Basic validation

### Data Management
- Fetch element data from existing API endpoints
- Use Pinia for state management
- Standard loading/error states
- Optimistic updates for better UX

### Accessibility
- Proper ARIA labels
- Keyboard navigation support
- Screen reader friendly
- High contrast support

These DDFE views integrate seamlessly with the existing test automation platform UI and share the same design system and patterns.

## Vue.js Implementation Guidelines

### Single File Components (SFC)

Use Vue 3 Composition API with `<script setup>`:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  title: string;
  items: Array<{ id: string; name: string }>;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  select: [id: string];
}>();

const searchQuery = ref('');

const filteredItems = computed(() => {
  return props.items.filter(item =>
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const handleSelect = (id: string) => {
  emit('select', id);
};
</script>

<template>
  <div class="container">
    <h2>{{ title }}</h2>
    <input v-model="searchQuery" placeholder="Search..." />
    <ul>
      <li v-for="item in filteredItems" :key="item.id" @click="handleSelect(item.id)">
        {{ item.name }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.container {
  padding: 1rem;
}
</style>
```

### State Management with Pinia

```typescript
// stores/elementsStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Element } from '@/types';

export const useElementsStore = defineStore('elements', () => {
  const elements = ref<Element[]>([]);
  const selectedElement = ref<Element | null>(null);
  const loading = ref(false);

  const getElementById = computed(() => (id: string) => {
    return elements.value.find(el => el.id === id);
  });

  async function fetchElements() {
    loading.value = true;
    try {
      const response = await fetch('/api/elements');
      elements.value = await response.json();
    } finally {
      loading.value = false;
    }
  }

  function selectElement(element: Element) {
    selectedElement.value = element;
  }

  return {
    elements,
    selectedElement,
    loading,
    getElementById,
    fetchElements,
    selectElement,
  };
});
```

### Composables for Reusable Logic

```typescript
// composables/useElementFilters.ts
import { ref, computed } from 'vue';

export function useElementFilters(elements: Ref<Element[]>) {
  const searchQuery = ref('');
  const filterType = ref<string | null>(null);

  const filteredElements = computed(() => {
    return elements.value.filter(element => {
      const matchesSearch = element.name
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase());
      const matchesType = !filterType.value || element.type === filterType.value;
      return matchesSearch && matchesType;
    });
  });

  return {
    searchQuery,
    filterType,
    filteredElements,
  };
}
```

### Testing with Vitest

```typescript
// components/__tests__/ElementBrowser.spec.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ElementBrowser from '../ElementBrowser.vue';

describe('ElementBrowser', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('renders element list', () => {
    const wrapper = mount(ElementBrowser, {
      props: {
        elements: [
          { id: '1', name: 'Button', type: 'button' },
          { id: '2', name: 'Input', type: 'input' },
        ],
      },
    });

    expect(wrapper.text()).toContain('Button');
    expect(wrapper.text()).toContain('Input');
  });

  it('filters elements by search query', async () => {
    const wrapper = mount(ElementBrowser, {
      props: {
        elements: [
          { id: '1', name: 'Button', type: 'button' },
          { id: '2', name: 'Input', type: 'input' },
        ],
      },
    });

    await wrapper.find('input[type="search"]').setValue('Button');
    expect(wrapper.text()).toContain('Button');
    expect(wrapper.text()).not.toContain('Input');
  });
});
```

## Package Configuration

```json
{
  "name": "ai-test-automation-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "lint": "eslint . --ext .vue,.ts --fix"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
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
    "eslint-plugin-vue": "^9.18.1"
  }
}
```
