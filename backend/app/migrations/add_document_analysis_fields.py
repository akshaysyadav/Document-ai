"""Add summary and tasks fields to documents table

Revision ID: add_analysis_fields
Revises: 
Create Date: 2025-01-16 18:36:05.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_analysis_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add summary and tasks columns to documents table
    op.add_column('documents', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('tasks', sa.JSON(), nullable=True))


def downgrade():
    # Remove the added columns
    op.drop_column('documents', 'tasks')
    op.drop_column('documents', 'summary')