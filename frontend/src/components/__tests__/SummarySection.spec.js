import { flushPromises } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import SummarySection from '../SummarySection.vue'
import { getSummary } from '../../api'
import { apiError, mountWithElementPlus } from './helpers'

vi.mock('../../api', () => ({ getSummary: vi.fn() }))
vi.mock('element-plus', async (importOriginal) => ({
  ...(await importOriginal()),
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() }
}))

const generate = async (wrapper) => {
  await wrapper.find('.generate-btn').trigger('click')
  await flushPromises()
}

describe('SummarySection', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows the empty state at first', () => {
    const wrapper = mountWithElementPlus(SummarySection)
    expect(wrapper.find('.empty-state').text()).toContain('Generate Summary')
  })

  it('shows the summary and numbered recommendations', async () => {
    getSummary.mockResolvedValue({
      data: { summary: 'A short summary.', recommendations: ['Paper A (2017)', 'Paper B (2018)'] }
    })
    const wrapper = mountWithElementPlus(SummarySection)

    await generate(wrapper)

    expect(wrapper.find('.summary-text').text()).toBe('A short summary.')
    expect(wrapper.findAll('.rec-number').map((item) => item.text())).toEqual(['1.', '2.'])
    expect(wrapper.findAll('.rec-text').map((item) => item.text())).toEqual(['Paper A (2017)', 'Paper B (2018)'])
    expect(ElMessage.success).toHaveBeenCalled()
  })

  it('says when there are no recommendations', async () => {
    getSummary.mockResolvedValue({ data: { summary: 'A short summary.', recommendations: [] } })
    const wrapper = mountWithElementPlus(SummarySection)

    await generate(wrapper)

    expect(wrapper.find('.empty-recommendations').text()).toBe('No recommendations available')
  })

  it('shows the backend error message when generation fails', async () => {
    getSummary.mockRejectedValue(apiError(400, { error: 'No paper selected. Please upload a PDF first.' }))
    const wrapper = mountWithElementPlus(SummarySection)

    await generate(wrapper)

    expect(ElMessage.error).toHaveBeenCalledWith('No paper selected. Please upload a PDF first.')
    expect(ElMessage.success).not.toHaveBeenCalled()
    expect(wrapper.find('.summary-box').exists()).toBe(false)
  })
})
