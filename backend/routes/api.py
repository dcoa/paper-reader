import hashlib

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from services import PDFProcessor, MetadataExtractor, Embedder, VectorStore, RAGEngine, Summarizer

api_bp = Blueprint('api', __name__)

pdf_processor = PDFProcessor()
metadata_extractor = MetadataExtractor()
embedder = Embedder()
vector_store = VectorStore()
rag_engine = RAGEngine(vector_store=vector_store)
summarizer = Summarizer()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def duplicate_response(filename, existing):
    # Use the stored paper for Q&A and summaries instead of adding it again
    vector_store.set_active_paper(existing['metadata'])
    return jsonify({
        'error': 'This paper is already in the knowledge base',
        'duplicate': True,
        'filename': filename,
        'metadata': existing['metadata'],
        'num_chunks': existing['num_chunks']
    }), 409

@api_bp.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    try:
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        existing = vector_store.find_by_hash(file_hash)
        if existing:
            return duplicate_response(filename, existing)

        filepath = Config.UPLOAD_FOLDER / filename
        filepath.write_bytes(file_bytes)

        pdf_result = pdf_processor.process_pdf(
            str(filepath),
            chunk_size=Config.CHUNK_SIZE,
            overlap=Config.CHUNK_OVERLAP
        )
        metadata = metadata_extractor.extract_metadata(pdf_result['cleaned_text'])

        # Same paper stored from a different file (or preloaded from arXiv)
        existing = vector_store.find_by_title(metadata.get('title'))
        if existing:
            return duplicate_response(filename, existing)

        metadata['file_hash'] = file_hash
        vectors = embedder.embed_documents(pdf_result['chunks'])

        vector_store.add_documents(
            documents=pdf_result['chunks'],
            vectors=vectors,
            metadata=metadata
        )

        return jsonify({
            'message': 'PDF uploaded and processed successfully',
            'filename': filename,
            'metadata': metadata,
            'num_chunks': pdf_result['num_chunks']
        }), 200

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@api_bp.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()

    if not data or 'question' not in data:
        return jsonify({'error': 'Missing question parameter'}), 400

    question = data['question']

    try:
        result = rag_engine.answer_question(question, top_k=Config.TOP_K)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Q&A failed: {str(e)}'}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = vector_store.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@api_bp.route('/clear', methods=['POST'])
def clear_database():
    try:
        vector_store.clear()
        return jsonify({'message': 'Knowledge base cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear: {str(e)}'}), 500

@api_bp.route('/summarize', methods=['POST'])
def summarize_paper():
    try:
        stats = vector_store.get_stats()
        if stats['total_documents'] == 0:
            return jsonify({'error': 'No documents in knowledge base. Please upload a PDF first.'}), 400

        full_text, latest_metadata = vector_store.get_latest_document()
        full_embedding = embedder.embed_query(full_text)
        recomended_papers = vector_store.get_recommended_papers(full_embedding, top_k=10)
        recomended_papers_string = ""
        for paper in recomended_papers:
            title = paper.get('title', 'N/A')
            authors = paper.get('authors', 'N/A')
            year = paper.get('year', 'N/A') 
            abstract = paper.get('abstract', 'N/A')
            sim_score = paper.get('score', 0)
            recomended_papers_string += f"- {title} by {authors} ({year})  - { abstract } (Relevance: { sim_score }) \n"
        result = summarizer.generate_summary_and_recommendations(latest_metadata, full_text, recomended_papers_string)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500

