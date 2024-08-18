"""changed

Revision ID: 977914e72076
Revises: d803c7eb0fab
Create Date: 2024-08-17 12:59:55.671957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '977914e72076'
down_revision = 'd803c7eb0fab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.execute("""
        ALTER TABLE blum_account 
        ALTER COLUMN "availableBalance" TYPE FLOAT 
        USING "availableBalance"::double precision;
    """)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blum_account', 'availableBalance',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###
