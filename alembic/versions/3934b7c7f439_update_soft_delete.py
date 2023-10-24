"""update soft delete

Revision ID: 3934b7c7f439
Revises: 808b0c2a3d9b
Create Date: 2023-10-24 15:33:54.278164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '3934b7c7f439'
down_revision: Union[str, None] = '808b0c2a3d9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'deleted_at',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='删除时间',
               existing_nullable=True)
    op.drop_column('users', 'is_deleted')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True, comment='软删除标志'))
    op.alter_column('users', 'deleted_at',
               existing_type=mysql.DATETIME(),
               comment='删除时间',
               existing_nullable=True)
    # ### end Alembic commands ###