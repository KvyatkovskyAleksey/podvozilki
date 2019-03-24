"""1

Revision ID: b2f70c7600eb
Revises: 
Create Date: 2018-12-10 09:51:33.839709

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f70c7600eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('trip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trip_from', sa.String(length=120), nullable=True),
    sa.Column('trip_to', sa.String(length=120), nullable=True),
    sa.Column('trip_time', sa.DateTime(), nullable=True),
    sa.Column('free_seats', sa.Integer(), nullable=True),
    sa.Column('driver_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['driver_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trip_trip_time'), 'trip', ['trip_time'], unique=False)
    op.create_table('users_trips',
    sa.Column('user', sa.Integer(), nullable=True),
    sa.Column('trip', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['trip'], ['trip.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_trips')
    op.drop_index(op.f('ix_trip_trip_time'), table_name='trip')
    op.drop_table('trip')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
