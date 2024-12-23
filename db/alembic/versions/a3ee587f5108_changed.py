"""changed

Revision ID: a3ee587f5108
Revises: b081934bb98e
Create Date: 2024-06-29 21:23:46.250983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3ee587f5108'
down_revision = 'b081934bb98e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_invoice', sa.Column('errorStatus', sa.String(), nullable=True))
    op.add_column('order_invoice', sa.Column('network', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_invoice', 'network')
    op.drop_column('order_invoice', 'errorStatus')
    # ### end Alembic commands ###
