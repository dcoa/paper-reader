from conftest import make_pdf
from services.pdf_processor import PDFProcessor


def test_clean_text_collapses_whitespace_and_removes_symbols():
    assert PDFProcessor.clean_text('  Deep   learning\n\tis #fun@  ') == 'Deep learning is fun'


def test_clean_text_keeps_punctuation():
    assert PDFProcessor.clean_text('Results: 95%, (p < 0.05).') == 'Results: 95, (p  0.05).'


def test_split_into_chunks_overlaps_consecutive_chunks():
    words = [f'w{i}' for i in range(25)]
    chunks = PDFProcessor.split_into_chunks(' '.join(words), chunk_size=10, overlap=2)

    assert chunks[0].split() == words[0:10]
    assert chunks[1].split() == words[8:18]
    assert chunks[2].split() == words[16:25]
    assert chunks[3].split() == words[24:25]


def test_split_into_chunks_short_text_is_one_chunk():
    assert PDFProcessor.split_into_chunks('just a few words', chunk_size=10, overlap=2) == ['just a few words']


def test_split_into_chunks_empty_text():
    assert PDFProcessor.split_into_chunks('', chunk_size=10, overlap=2) == []


def test_process_pdf_extracts_cleans_and_chunks(tmp_path):
    pdf_path = tmp_path / 'paper.pdf'
    pdf_path.write_bytes(make_pdf('Attention Is All You Need', 'We propose the Transformer.'))

    result = PDFProcessor().process_pdf(str(pdf_path), chunk_size=500, overlap=50)

    assert 'Attention Is All You Need' in result['cleaned_text']
    assert 'Transformer' in result['cleaned_text']
    assert result['num_chunks'] == len(result['chunks']) == 1
