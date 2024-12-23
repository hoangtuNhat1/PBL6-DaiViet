"""modify payment_name

Revision ID: 544e35710a2f
Revises: 9a22147eb830
Create Date: 2024-12-03 22:58:15.824158

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "544e35710a2f"
down_revision: Union[str, None] = "9a22147eb830"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "cancelled", name="order_status_enum"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_accounts.uid"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("purchase_orders")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "purchase_orders",
        sa.Column("id", mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", mysql.VARCHAR(length=36), nullable=False),
        sa.Column("amount", mysql.FLOAT(), nullable=False),
        sa.Column(
            "status", mysql.ENUM("pending", "completed", "cancelled"), nullable=False
        ),
        sa.Column(
            "created_at",
            mysql.TIMESTAMP(),
            server_default=sa.text("(now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.TIMESTAMP(),
            server_default=sa.text("(now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user_accounts.uid"], name="purchase_orders_ibfk_1"
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.drop_table("payments")
    # ### end Alembic commands ###
