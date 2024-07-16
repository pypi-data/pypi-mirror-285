"""Add topic 3

Revision ID: 27086791044c
Revises: e02c90ea67bb
Create Date: 2024-07-11 13:15:45.273275

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27086791044c"
down_revision: Union[str, None] = "e02c90ea67bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "arbitrum_one_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    op.add_column(
        "arbitrum_sepolia_logs",
        sa.Column("topic3", sa.VARCHAR(length=256), nullable=True),
    )
    op.add_column(
        "ethereum_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    op.add_column(
        "game7_orbit_arbitrum_sepolia_logs",
        sa.Column("topic3", sa.VARCHAR(length=256), nullable=True),
    )
    op.add_column(
        "mantle_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    op.add_column(
        "mantle_sepolia_logs",
        sa.Column("topic3", sa.VARCHAR(length=256), nullable=True),
    )
    op.add_column(
        "polygon_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    op.add_column(
        "xai_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    op.add_column(
        "xai_sepolia_logs", sa.Column("topic3", sa.VARCHAR(length=256), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("xai_sepolia_logs", "topic3")
    op.drop_column("xai_logs", "topic3")
    op.drop_column("polygon_logs", "topic3")
    op.drop_column("mantle_sepolia_logs", "topic3")
    op.drop_column("mantle_logs", "topic3")
    op.drop_column("game7_orbit_arbitrum_sepolia_logs", "topic3")
    op.drop_column("ethereum_logs", "topic3")
    op.drop_column("arbitrum_sepolia_logs", "topic3")
    op.drop_column("arbitrum_one_logs", "topic3")
    # ### end Alembic commands ###
