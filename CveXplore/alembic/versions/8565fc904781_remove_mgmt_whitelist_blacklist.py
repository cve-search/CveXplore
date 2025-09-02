"""remove mgmt whitelist/blacklist

Revision ID: 8565fc904781
Revises: 0dc1d3ca2560
Create Date: 2025-09-02 16:11:21.838893

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8565fc904781"
down_revision: Union[str, None] = "0dc1d3ca2560"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_mgmt_blacklist_id", table_name="mgmt_blacklist")
    op.drop_table("mgmt_blacklist")
    op.drop_index("ix_mgmt_whitelist_id", table_name="mgmt_whitelist")
    op.drop_table("mgmt_whitelist")


def downgrade() -> None:
    op.create_table(
        "mgmt_whitelist",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mgmt_whitelist_id", "mgmt_whitelist", ["id"], unique=False)
    op.create_table(
        "mgmt_blacklist",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mgmt_blacklist_id", "mgmt_blacklist", ["id"], unique=False)
