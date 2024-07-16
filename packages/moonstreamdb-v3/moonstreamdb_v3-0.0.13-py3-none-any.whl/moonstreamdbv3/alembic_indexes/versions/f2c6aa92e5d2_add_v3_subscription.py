"""Add v3 subscription

Revision ID: f2c6aa92e5d2
Revises: 27086791044c
Create Date: 2024-07-11 19:41:49.899157

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2c6aa92e5d2"
down_revision: Union[str, None] = "27086791044c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "abi_subscriptions",
        sa.Column("abi_job_id", sa.UUID(), nullable=False),
        sa.Column("subscription_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', statement_timestamp())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["abi_job_id"],
            ["abi_jobs.id"],
            name=op.f("fk_abi_subscriptions_abi_job_id_abi_jobs"),
        ),
        sa.PrimaryKeyConstraint(
            "abi_job_id", "subscription_id", name=op.f("pk_abi_subscriptions")
        ),
    )
    op.create_index(
        op.f("ix_abi_subscriptions_abi_job_id"),
        "abi_subscriptions",
        ["abi_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_abi_subscriptions_subscription_id"),
        "abi_subscriptions",
        ["subscription_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_abi_subscriptions_subscription_id"), table_name="abi_subscriptions"
    )
    op.drop_index(
        op.f("ix_abi_subscriptions_abi_job_id"), table_name="abi_subscriptions"
    )
    op.drop_table("abi_subscriptions")
    # ### end Alembic commands ###
