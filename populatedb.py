# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category

engine = create_engine('postgresql://catalog:catalog@localhost/itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# engine.execute("drop table user;")
# engine.execute("drop table category;")
# engine.execute("drop table items;")

cat1 = Category(name="Children's Literature")
session.add(cat1)
session.commit()

cat2 = Category(name="Computers & Technology")
session.add(cat2)
session.commit()

cat3 = Category(name="Science Fiction & Fantasy")
session.add(cat3)
session.commit()

cat4 = Category(name="Mystery, Suspense & Thriller")
session.add(cat4)
session.commit()

cat5 = Category(name="Engineering & Transporation")
session.add(cat5)
session.commit()

cat6 = Category(name="Health & Fitness")
session.add(cat6)
session.commit()

cat7 = Category(name="Crafts, Hobbies & Home")
session.add(cat7)
session.commit()

cat8 = Category(name="Science & Math")
session.add(cat8)
session.commit()

cat9 = Category(name="Travel")
session.add(cat9)
session.commit()

cat10 = Category(name="Others")
session.add(cat10)
session.commit()

session.close()

print "Populated book catalog!"
