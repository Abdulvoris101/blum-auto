"""port changed type

Revision ID: 924137209a79
Revises: 5e28b1914b88
Create Date: 2024-08-22 22:32:49.591363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '924137209a79'
down_revision = '5e28b1914b88'
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.execute('ALTER TABLE proxy ALTER COLUMN port TYPE INTEGER USING port::integer;')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('proxy', 'port',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###
