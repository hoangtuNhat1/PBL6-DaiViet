"""fix_payment_amount_field

Revision ID: 48b02dbc4f89
Revises: cd4617d61496
Create Date: 2024-12-04 20:57:29.931195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '48b02dbc4f89'
down_revision: Union[str, None] = 'cd4617d61496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('payments', 'amount',
               existing_type=mysql.ENUM('two_hundred', 'five_hundred', 'one_million', 'two_million'),
               type_=sa.Integer(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('payments', 'amount',
               existing_type=sa.Integer(),
               type_=mysql.ENUM('two_hundred', 'five_hundred', 'one_million', 'two_million'),
               existing_nullable=False)
    # ### end Alembic commands ###
