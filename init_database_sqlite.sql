-- Paper Reader SQLite Database Initialization Script
-- This script creates all necessary tables for the Paper Reader application

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- 1. Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    status INTEGER DEFAULT 1
);

-- 2. Create publication_types table
CREATE TABLE IF NOT EXISTS publication_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create papers table
CREATE TABLE IF NOT EXISTS papers (
    paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    publication_type_id INTEGER,
    publication_name TEXT,
    year INTEGER,
    abstract TEXT,
    keywords TEXT,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    upload_user_id INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1,
    FOREIGN KEY (publication_type_id) REFERENCES publication_types(type_id),
    FOREIGN KEY (upload_user_id) REFERENCES users(user_id)
);

-- 4. Create annotations table
CREATE TABLE IF NOT EXISTS annotations (
    annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    section TEXT,
    page_number INTEGER,
    position_x INTEGER,
    position_y INTEGER,
    content TEXT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 5. Create ai_conversations table
CREATE TABLE IF NOT EXISTS ai_conversations (
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    context TEXT,
    model TEXT DEFAULT 'gpt-4',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 6. Create user_tokens table
CREATE TABLE IF NOT EXISTS user_tokens (
    token_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_time TIMESTAMP NOT NULL,
    status INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 7. Create paper_analysis table
CREATE TABLE IF NOT EXISTS paper_analysis (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL UNIQUE,
    summary TEXT,
    methodology TEXT,
    experiments TEXT,
    key_findings TEXT,
    full_content TEXT,
    analysis_status TEXT DEFAULT 'not_started',
    model_used TEXT DEFAULT 'deepseek-reasoner',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_papers_publication_type_id ON papers(publication_type_id);
CREATE INDEX IF NOT EXISTS idx_papers_upload_user_id ON papers(upload_user_id);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_upload_time ON papers(upload_time);

CREATE INDEX IF NOT EXISTS idx_annotations_paper_id ON annotations(paper_id);
CREATE INDEX IF NOT EXISTS idx_annotations_user_id ON annotations(user_id);
CREATE INDEX IF NOT EXISTS idx_annotations_create_time ON annotations(create_time);

CREATE INDEX IF NOT EXISTS idx_ai_conversations_paper_id ON ai_conversations(paper_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_create_time ON ai_conversations(create_time);

CREATE INDEX IF NOT EXISTS idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tokens_expire_time ON user_tokens(expire_time);

CREATE INDEX IF NOT EXISTS idx_paper_analysis_paper_id ON paper_analysis(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_analysis_status ON paper_analysis(analysis_status);

-- Insert default data
-- Insert default users
INSERT OR IGNORE INTO users (username, password, email, role) VALUES
('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin@example.com', 'admin'),
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user1@example.com', 'user'),
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'user2@example.com', 'user');

-- Insert default publication types
INSERT OR IGNORE INTO publication_types (type_name) VALUES 
('Journal'),
('Conference'),
('Book'),
('Report'),
('Thesis');

