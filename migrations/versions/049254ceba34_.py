"""empty message

Revision ID: 049254ceba34
Revises: c2827d600d39
Create Date: 2024-08-25 21:37:46.914495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '049254ceba34'
down_revision = 'c2827d600d39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chapters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('chapter')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chapter',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('filename', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('book_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], name='chapter_book_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='chapter_pkey')
    )
    op.drop_table('chapters')
    # ### end Alembic commands ###