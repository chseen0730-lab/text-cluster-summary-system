<template>
  <div class="form-group" :class="{ error: !!errorMsg, focused }">
    <label v-if="label" class="form-label">{{ label }}<span v-if="required" class="required">*</span></label>
    <div class="input-wrap">
      <input
        v-if="type !== 'textarea'"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        class="form-input"
        @input="onInput"
        @focus="focused = true"
        @blur="onBlur"
      />
      <textarea
        v-else
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :rows="rows"
        class="form-input form-textarea"
        @input="onInput"
        @focus="focused = true"
        @blur="onBlur"
      />
    </div>
    <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>
    <p v-else-if="hint" class="form-hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  hint: { type: String, default: '' },
  rows: { type: Number, default: 4 },
  rules: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])
const focused = ref(false)
const errorMsg = ref('')

function validate(val) {
  for (const rule of props.rules) {
    if (rule.required && !val) {
      errorMsg.value = rule.message || '此字段为必填项'
      return false
    }
    if (rule.min && val.length < rule.min) {
      errorMsg.value = rule.message || `至少输入 ${rule.min} 个字符`
      return false
    }
    if (rule.max && val.length > rule.max) {
      errorMsg.value = rule.message || `最多输入 ${rule.max} 个字符`
      return false
    }
    if (rule.pattern && !rule.pattern.test(val)) {
      errorMsg.value = rule.message || '格式不正确'
      return false
    }
  }
  errorMsg.value = ''
  return true
}

function onInput(e) {
  const val = e.target.value
  emit('update:modelValue', val)
  if (errorMsg.value) validate(val)
}

function onBlur() {
  focused.value = false
  validate(props.modelValue)
}

defineExpose({ validate: () => validate(props.modelValue) })
</script>

<style scoped>
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.input-wrap {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.08);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.error .form-input {
  border-color: rgba(239, 68, 68, 0.5);
}

.error .form-input:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-error {
  color: #ef4444;
  font-size: 12px;
  margin-top: 6px;
}

.form-hint {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  margin-top: 6px;
}
</style>
