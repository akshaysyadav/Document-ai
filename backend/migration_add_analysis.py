"""Add document analysis fields

Revision ID: add_analysis_fields
Revises: 
Create Date: 2025-09-17 00:27:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_analysis_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add summary and tasks columns to documents table
    op.add_column('documents', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('tasks', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove summary and tasks columns
    op.drop_column('documents', 'tasks')
    op.drop_column('documents', 'summary')