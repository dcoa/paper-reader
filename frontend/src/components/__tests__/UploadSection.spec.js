import { flushPromises } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import UploadSection from '../UploadSection.vue'
import { uploadPDF } from '../../api'
import { apiError, mountWithElementPlus } from './helpers'

vi.mock('../../api', () => ({ uploadPDF: vi.fn() }))
vi.mock('element-plus', async (importOriginal) => ({
  ...(await importOriginal()),
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() }
}))

const metadata = {
  title: 'Attention Is All You Need',
  authors: ['Ashish Vaswani', 'Noam Shazeer'],
  keywords: ['transformer'],
  year: '2017'
}

const chooseFile = async (wrapper) => {
  const file = new File(['%PDF'], 'paper.pdf', { type: 'application/pdf' })
  wrapper.findComponent({ name: 'ElUpload' }).props('onChange')({ raw: file })
  await flushPromises()
  return file
}

const processFile = async (wrapper) => {
  await wrapper.find('.process-btn').trigger('click')
  await flushPromises()
}

describe('UploadSection', () => {
  beforeEach(() => vi.clearAllMocks())

  it('disables processing until a file is chosen', async () => {
    const wrapper = mountWithElementPlus(UploadSection)
    expect(wrapper.find('.process-btn').attributes('disabled')).toBeDefined()

    await chooseFile(wrapper)

    expect(wrapper.find('.process-btn').attributes('disabled')).toBeUndefined()
  })

  it('shows the result and notifies the app after a successful upload', async () => {
    uploadPDF.mockResolvedValue({ data: { filename: 'paper.pdf', metadata, num_chunks: 3 } })
    const wrapper = mountWithElementPlus(UploadSection)
    const file = await chooseFile(wrapper)

    await processFile(wrapper)

    expect(uploadPDF).toHaveBeenCalledWith(file, expect.any(Function))
    const result = wrapper.find('.upload-result')
    expect(result.text()).toContain('Processing Result')
    expect(result.text()).toContain('Attention Is All You Need')
    expect(result.text()).toContain('Ashish Vaswani, Noam Shazeer')
    expect(result.classes()).not.toContain('duplicate')
    expect(ElMessage.success).toHaveBeenCalled()
    expect(wrapper.emitted('upload-success')).toHaveLength(1)
  })

  it('shows the stored paper when it is already in the database', async () => {
    uploadPDF.mockRejectedValue(apiError(409, {
      error: 'This paper is already in the knowledge base',
      duplicate: true,
      filename: 'paper.pdf',
      metadata,
      num_chunks: 3
    }))
    const wrapper = mountWithElementPlus(UploadSection)
    await chooseFile(wrapper)

    await processFile(wrapper)

    const result = wrapper.find('.upload-result')
    expect(result.classes()).toContain('duplicate')
    expect(result.text()).toContain('Paper Already in Database')
    expect(result.text()).toContain('Attention Is All You Need')
    expect(result.text()).toContain('2017')
    expect(ElMessage.warning).toHaveBeenCalledWith('This paper is already in the knowledge base')
    expect(ElMessage.error).not.toHaveBeenCalled()
    expect(wrapper.emitted('upload-success')).toBeUndefined()
  })

  it('shows the backend error message when processing fails', async () => {
    uploadPDF.mockRejectedValue(apiError(500, {
      error: 'The PDF could not be processed. Please try again later.'
    }))
    const wrapper = mountWithElementPlus(UploadSection)
    await chooseFile(wrapper)

    await processFile(wrapper)

    expect(ElMessage.error).toHaveBeenCalledWith('The PDF could not be processed. Please try again later.')
    expect(wrapper.find('.upload-result').exists()).toBe(false)
    expect(wrapper.find('.process-btn').text()).toBe('Start Processing')
  })
})
