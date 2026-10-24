import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'

export const mountWithElementPlus = (component) => mount(component, {
  global: { plugins: [ElementPlus] }
})

// Rejected axios request with the given status and response body
export const apiError = (status, data) => Object.assign(new Error('Request failed'), {
  response: { status, data }
})
