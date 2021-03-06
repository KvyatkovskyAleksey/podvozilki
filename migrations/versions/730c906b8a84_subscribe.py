"""Subscribe

Revision ID: 730c906b8a84
Revises: f0d00f4a2444
Create Date: 2019-01-23 18:16:08.583297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '730c906b8a84'
down_revision = 'f0d00f4a2444'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscribe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('subscription_info', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscribe')
    # ### end Alembic commands ###
