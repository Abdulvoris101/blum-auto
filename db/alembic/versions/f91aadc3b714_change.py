"""change

Revision ID: f91aadc3b714
Revises: c3a085e993c8
Create Date: 2024-08-23 11:36:30.621190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f91aadc3b714'
down_revision = 'c3a085e993c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account_subscription', sa.Column('isFreeTrial', sa.Boolean(), nullable=True))
    op.drop_column('account_subscription', 'isGrantGiven')
    op.add_column('user', sa.Column('isGrantGiven', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'isGrantGiven')
    op.add_column('account_subscription', sa.Column('isGrantGiven', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('account_subscription', 'isFreeTrial')
    # ### end Alembic commands ###