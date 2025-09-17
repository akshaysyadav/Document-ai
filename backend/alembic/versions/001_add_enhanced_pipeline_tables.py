"""Add enhanced pipeline tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status and processed_at columns to documents table
    op.add_column('documents', sa.Column('status', sa.String(), nullable=True, server_default='uploaded'))
    op.add_column('documents', sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_documents_status', 'documents', ['status'])
    
    # Create chunks table
    op.create_table('chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=True),
        sa.Column('page_no', sa.Integer(), nullable=True),
        sa.Column('chunk_no', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('text_excerpt', sa.Text(), nullable=False),
        sa.Column('embedding_id', sa.String(), nullable=True),
        sa.Column('embedding_dim', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('nlp_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chunks_doc_id'), 'chunks', ['doc_id'])
    op.create_index(op.f('ix_chunks_page_no'), 'chunks', ['page_no'])
    op.create_index(op.f('ix_chunks_chunk_no'), 'chunks', ['chunk_no'])
    op.create_index(op.f('ix_chunks_embedding_id'), 'chunks', ['embedding_id'])
    op.create_index(op.f('ix_chunks_status'), 'chunks', ['status'])
    
    # Create summaries table
    op.create_table('summaries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Enum('DOCUMENT', 'CHAPTER', 'CHUNK', name='summarylevel'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_summaries_doc_id'), 'summaries', ['doc_id'])
    op.create_index(op.f('ix_summaries_level'), 'summaries', ['level'])
    
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('doc_id', sa.Integer(), nullable=True),
        sa.Column('source_chunk_id', sa.String(), nullable=True),
        sa.Column('task_text', sa.Text(), nullable=False),
        sa.Column('assignee', sa.String(), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority'), nullable=True, server_default='MEDIUM'),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'DONE', name='taskstatus'), nullable=True, server_default='OPEN'),
        sa.Column('extracted_by', sa.String(), nullable=False),
        sa.Column('task_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['doc_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_doc_id'), 'tasks', ['doc_id'])
    op.create_index(op.f('ix_tasks_source_chunk_id'), 'tasks', ['source_chunk_id'])
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'])
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'])


def downgrade() -> None:
    # Drop tasks table
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_priority'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_source_chunk_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_doc_id'), table_name='tasks')
    op.drop_table('tasks')
    
    # Drop summaries table
    op.drop_index(op.f('ix_summaries_level'), table_name='summaries')
    op.drop_index(op.f('ix_summaries_doc_id'), table_name='summaries')
    op.drop_table('summaries')
    
    # Drop chunks table
    op.drop_index(op.f('ix_chunks_status'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_embedding_id'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_chunk_no'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_page_no'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_doc_id'), table_name='chunks')
    op.drop_table('chunks')
    
    # Remove columns from documents table
    op.drop_index('ix_documents_status', table_name='documents')
    op.drop_column('documents', 'processed_at')
    op.drop_column('documents', 'status')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS taskpriority')
    op.execute('DROP TYPE IF EXISTS summarylevel')
