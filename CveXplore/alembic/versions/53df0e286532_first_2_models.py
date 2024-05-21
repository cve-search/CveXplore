"""First 2 models

Revision ID: 53df0e286532
Revises: 
Create Date: 2023-12-20 16:18:04.244419

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "53df0e286532"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("db", sa.String(length=25), nullable=True),
        sa.Column("lastModified", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "schema",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rebuild_needed", sa.Boolean(), nullable=True),
        sa.Column("version", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("schema")
    op.drop_table("info")
    # ### end Alembic commands ###