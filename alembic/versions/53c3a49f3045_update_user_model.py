"""update user model

Revision ID: 53c3a49f3045
Revises: 1da7c11caecf
Create Date: 2023-10-24 11:28:53.305757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '53c3a49f3045'
down_revision: Union[str, None] = '1da7c11caecf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=False, comment='电子邮件'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='创建日期'))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True, comment='最后更新日期'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True, comment='最后登录时间'))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=True, comment='软删除标志'))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间'))
    op.alter_column('users', 'name',
               existing_type=mysql.VARCHAR(length=255),
               comment='姓名',
               existing_nullable=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.alter_column('users', 'name',
               existing_type=mysql.VARCHAR(length=255),
               comment=None,
               existing_comment='姓名',
               existing_nullable=True)
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###
