"""fase 2 - exchange engine e payment callbacks

Revision ID: a1b2c3d4e5f6
Revises: 77d17bf6b79c
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '77d17bf6b79c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'exchange_rates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),
        sa.Column('quote_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('base_currency', 'quote_currency', name='uq_exchange_rate_pair'),
    )

    op.create_table(
        'exchange_rate_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),
        sa.Column('quote_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment_callbacks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('deposit_id', sa.UUID(), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('external_reference', sa.String(length=150), nullable=True),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('signature_valid', sa.Boolean(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['deposit_id'], ['deposits.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_payment_callbacks_external_reference'),
        'payment_callbacks',
        ['external_reference'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_payment_callbacks_external_reference'), table_name='payment_callbacks')
    op.drop_table('payment_callbacks')
    op.drop_table('exchange_rate_history')
    op.drop_table('exchange_rates')
