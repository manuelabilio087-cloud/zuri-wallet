"""fase 3 - levantamentos via binance

Revision ID: c7e9f1a2b3d4
Revises: a1b2c3d4e5f6
Create Date: 2026-09-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7e9f1a2b3d4'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'withdrawals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('asset', sa.String(length=10), nullable=False),
        sa.Column('network', sa.String(length=20), nullable=False),
        sa.Column('destination_address', sa.String(length=200), nullable=False),
        sa.Column(
            'status',
            sa.Enum('pending', 'processing', 'completed', 'failed', name='withdrawalstatus'),
            nullable=False,
            server_default='pending',
        ),
        sa.Column('binance_withdrawal_id', sa.String(length=100), nullable=True),
        sa.Column('provider_response', sa.String(length=1000), nullable=True),
        sa.Column('failure_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_withdrawals_binance_withdrawal_id'), 'withdrawals', ['binance_withdrawal_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_withdrawals_binance_withdrawal_id'), table_name='withdrawals')
    op.drop_table('withdrawals')
    sa.Enum(name='withdrawalstatus').drop(op.get_bind(), checkfirst=True)
