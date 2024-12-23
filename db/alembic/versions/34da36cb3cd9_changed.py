"""changed

Revision ID: 34da36cb3cd9
Revises: ac946d6936b2
Create Date: 2024-08-18 15:11:51.994928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34da36cb3cd9'
down_revision = 'ac946d6936b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account_subscription', sa.Column('isCanceled', sa.Boolean(), nullable=True))
    op.add_column('account_subscription', sa.Column('canceledAt', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account_subscription', 'canceledAt')
    op.drop_column('account_subscription', 'isCanceled')
    # ### end Alembic commands ###
