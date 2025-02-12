"""Removed lane opponenet

Revision ID: a6d465e8dd50
Revises: e9965940ba8e
Create Date: 2025-01-27 21:03:42.733145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6d465e8dd50'
down_revision = 'e9965940ba8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_column('opponent_lane_rank')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('opponent_lane_rank', sa.INTEGER(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
