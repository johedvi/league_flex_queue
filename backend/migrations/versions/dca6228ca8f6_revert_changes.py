"""Revert changes

Revision ID: dca6228ca8f6
Revises: a6d465e8dd50
Create Date: 2025-01-28 17:46:51.527054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dca6228ca8f6'
down_revision = 'a6d465e8dd50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('opponent_lane_rank', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_column('opponent_lane_rank')

    # ### end Alembic commands ###
