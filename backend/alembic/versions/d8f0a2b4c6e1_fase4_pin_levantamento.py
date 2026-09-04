"""fase 4 - pin de levantamento

Revision ID: d8f0a2b4c6e1
Revises: c7e9f1a2b3d4
Create Date: 2026-09-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd8f0a2b4c6e1'
down_revision: Union[str, Sequence[str], None] = 'c7e9f1a2b3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('transaction_pin_hash', sa.String(length=255), nullable=True))
    op.add_column(
        'users',
        sa.Column('pin_failed_attempts', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column('users', sa.Column('pin_locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'pin_locked_until')
    op.drop_column('users', 'pin_failed_attempts')
    op.drop_column('users', 'transaction_pin_hash')
