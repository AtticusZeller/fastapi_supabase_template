"""initial commit

Revision ID: 2c0516590c18
Revises:
Create Date: 2024-11-11 13:59:36.474238

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0516590c18'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('users',
    # sa.Column('id', sa.Uuid(), nullable=False),
    # sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    # sa.PrimaryKeyConstraint('id'),
    # schema='auth'
    # )
    op.create_table('item',
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['auth.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item')
    # op.drop_table('users', schema='auth')
    # ### end Alembic commands ###