"""migration2

Revision ID: ac2ae3cb6db9
Revises: 4c1f676a01aa
Create Date: 2025-02-17 20:43:22.077746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac2ae3cb6db9'
down_revision: Union[str, None] = '4c1f676a01aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_unique_constraint(None, 'notifications', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'notifications', type_='unique')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    # ### end Alembic commands ###
