import { flushPromises } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import QASection from '../QASection.vue'
import { askQuestion } from '../../api'
import { apiError, mountWithElementPlus } from './helpers'

vi.mock('../../api', () => ({ askQuestion: vi.fn() }))
vi.mock('element-plus', async (importOriginal) => ({
  ...(await importOriginal()),
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() }
}))

const ask = async (wrapper, question) => {
  await wrapper.find('input').setValue(question)
  await wrapper.find('.ask-btn').trigger('click')
  await flushPromises()
}

describe('QASection', () => {
  beforeEach(() => vi.clearAllMocks())

  it('starts with an empty conversation', () => {
    const wrapper = mountWithElementPlus(QASection)
    expect(wrapper.find('.empty-state').text()).toContain('Enter your question')
  })

  it('warns about an empty question without calling the API', async () => {
    const wrapper = mountWithElementPlus(QASection)

    await ask(wrapper, '   ')

    expect(ElMessage.warning).toHaveBeenCalledWith('Please enter a question')
    expect(askQuestion).not.toHaveBeenCalled()
  })

  it('shows the question, the answer and its sources', async () => {
    askQuestion.mockResolvedValue({
      data: {
        answer: 'The paper proposes the Transformer.',
        sources: [{
          document: 'We propose a new simple network architecture, the Transformer.',
          metadata: { title: 'Attention Is All You Need' },
          score: 0.1234
        }]
      }
    })
    const wrapper = mountWithElementPlus(QASection)

    await ask(wrapper, 'What does the paper propose?')

    expect(askQuestion).toHaveBeenCalledWith('What does the paper propose?')
    const messages = wrapper.findAll('.message')
    expect(messages).toHaveLength(2)
    expect(messages[0].classes()).toContain('user')
    expect(messages[0].text()).toContain('What does the paper propose?')
    expect(messages[1].classes()).toContain('assistant')
    expect(messages[1].text()).toContain('The paper proposes the Transformer.')
    expect(messages[1].find('.sources').text()).toContain('Attention Is All You Need')
    expect(messages[1].find('.score').text()).toBe('Relevance: 12.34%')
    expect(wrapper.find('input').element.value).toBe('')
  })

  it('shows an error and a fallback reply when answering fails', async () => {
    askQuestion.mockRejectedValue(apiError(500, {
      error: 'The question could not be answered. Please try again later.'
    }))
    const wrapper = mountWithElementPlus(QASection)

    await ask(wrapper, 'Q?')

    expect(ElMessage.error).toHaveBeenCalledWith('The question could not be answered. Please try again later.')
    const messages = wrapper.findAll('.message')
    expect(messages[1].text()).toContain('Sorry, an error occurred')
  })
})
