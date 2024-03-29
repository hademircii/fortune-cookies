"""enable autogenerate

Revision ID: 8c007b31ba3e
Revises: 
Create Date: 2023-07-29 19:38:34.683675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c007b31ba3e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_authors_id'), 'authors', ['id'], unique=False)
    op.create_index(op.f('ix_authors_name'), 'authors', ['name'], unique=True)
    op.create_table('phone_numbers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('hashed_phone_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phone_numbers_hashed_phone_number'), 'phone_numbers', ['hashed_phone_number'], unique=True)
    op.create_index(op.f('ix_phone_numbers_phone_number'), 'phone_numbers', ['phone_number'], unique=True)
    op.create_table('quotes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('hashed_text', sa.String(), nullable=True),
    sa.Column('reference', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hashed_text')
    )
    op.create_index(op.f('ix_quotes_author_id'), 'quotes', ['author_id'], unique=False)
    op.create_index(op.f('ix_quotes_id'), 'quotes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_quotes_id'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_author_id'), table_name='quotes')
    op.drop_table('quotes')
    op.drop_index(op.f('ix_phone_numbers_phone_number'), table_name='phone_numbers')
    op.drop_index(op.f('ix_phone_numbers_hashed_phone_number'), table_name='phone_numbers')
    op.drop_table('phone_numbers')
    op.drop_index(op.f('ix_authors_name'), table_name='authors')
    op.drop_index(op.f('ix_authors_id'), table_name='authors')
    op.drop_table('authors')
    # ### end Alembic commands ###
