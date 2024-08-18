"""changed

Revision ID: ac946d6936b2
Revises: 977914e72076
Create Date: 2024-08-17 20:46:38.923751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac946d6936b2'
down_revision = '977914e72076'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('isGrantGiven', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'isGrantGiven')
    # ### end Alembic commands ###
