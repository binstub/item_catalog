from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    picture = Column(String(250))


class Category(Base):
    # __tablename__ is a special variable that will be used for the tablename
    __tablename__ = "category"

    # define the columns of this table:
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    # 'bidirectional One-To-Many'-relationship
    items = relationship("Item",
                         order_by="Item.title",
                         back_populates="category")

    # Return object data in easily serializeable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name
            }


class Item(Base):
    # specify the tablename
    __tablename__ = "items"
    # Declare it's columns
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique=True)
    description = Column(String(1000))
    created_date = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="items")
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship(User)

    @property
    def serialize(self):
        return {
            'category.id': self.category_id,
            'id': self.id,
            'title': self.title,
            'description': self.description
        }


engine = create_engine('postgresql://catalog:catalog@localhost/itemcatalog.db')


Base.metadata.create_all(engine)
