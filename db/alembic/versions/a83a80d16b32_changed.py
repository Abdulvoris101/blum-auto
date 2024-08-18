"""changed

Revision ID: a83a80d16b32
Revises: 384dda6a9c98
Create Date: 2024-07-21 21:27:40.056368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a83a80d16b32'
down_revision = '384dda6a9c98'
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
