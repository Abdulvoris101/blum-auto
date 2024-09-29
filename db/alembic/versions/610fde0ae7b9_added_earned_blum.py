"""added earned blum

Revision ID: 610fde0ae7b9
Revises: 09014b1fb524
Create Date: 2024-09-22 14:57:55.424153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '610fde0ae7b9'
down_revision = '09014b1fb524'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blum_account', sa.Column('earnedBlumCoins', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('blum_account', 'earnedBlumCoins')
    # ### end Alembic commands ###