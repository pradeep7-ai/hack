"""Initial migration

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
    # Create documents table
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=True),
        sa.Column('embedding_status', sa.String(length=50), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)

    # Create queries table
    op.create_table('queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queries_id'), 'queries', ['id'], unique=False)

    # Create document_chunks table
    op.create_table('document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_id', sa.String(length=255), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('embedding_id', sa.String(length=255), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_chunk_id'), 'document_chunks', ['chunk_id'], unique=True)
    op.create_index(op.f('ix_document_chunks_id'), 'document_chunks', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_document_chunks_id'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_chunk_id'), table_name='document_chunks')
    op.drop_table('document_chunks')
    
    op.drop_index(op.f('ix_queries_id'), table_name='queries')
    op.drop_table('queries')
    
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents') 