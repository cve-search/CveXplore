"""Combined changes since init

Revision ID: 0dc1d3ca2560
Revises: ecb1788b7e08
Create Date: 2025-09-02 16:03:59.108933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0dc1d3ca2560"
down_revision: Union[str, None] = "ecb1788b7e08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_capec_id"), "capec", ["id"], unique=True)
    op.create_index(op.f("ix_capec_loa"), "capec", ["loa"], unique=False)
    op.create_index(op.f("ix_capec_name"), "capec", ["name"], unique=False)
    op.add_column("cves", sa.Column("cvss4", sa.Float(), nullable=True))
    op.add_column("cves", sa.Column("configurations", sa.JSON(), nullable=True))
    op.add_column("cves", sa.Column("cvss_data", sa.JSON(), nullable=True))
    op.drop_index("ix_cves_cwe", table_name="cves")
    op.create_index(op.f("ix_cves_cvss4"), "cves", ["cvss4"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cves_cvss4"), table_name="cves")
    op.create_index("ix_cves_cwe", "cves", ["cwe"], unique=False)
    op.drop_column("cves", "cvss_data")
    op.drop_column("cves", "configurations")
    op.drop_column("cves", "cvss4")
    op.drop_index(op.f("ix_capec_name"), table_name="capec")
    op.drop_index(op.f("ix_capec_loa"), table_name="capec")
    op.drop_index(op.f("ix_capec_id"), table_name="capec")
