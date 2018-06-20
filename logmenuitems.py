from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Company, Base, Gadgets, User

engine = create_engine('sqlite:///electronic.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="gayathri", email="15pa1a0553@vishnu.edu.in",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
restaurant1 = Company(user_id=1, name="LG")

session.add(restaurant1)
session.commit()

menuItem2 = Gadgets(user_id=1, name="Washing Machine", description="Long time ",
                     price="Rs.18900",item=restaurant1)

session.add(menuItem2)
session.commit()


menuItem1 = Gadgets(user_id=1, name="Television", description="32 inches",
                     price="Rs.14599",item=restaurant1)

session.add(menuItem1)
session.commit()

menuItem2 = Gadgets(user_id=1, name="Fridge", description="Double Door",
                     price="$Rs.25000",item=restaurant1)

session.add(menuItem2)
session.commit()

menuItem3 = Gadgets(user_id=1, name="Air Conditioner", description="More Efficent",
                     price="Rs.28000",item=restaurant1)

session.add(menuItem3)
session.commit()


# Menu for Super Stir Fry
restaurant2 = Company(user_id=1, name="SamSung")

session.add(restaurant2)
session.commit()


menuItem1 = Gadgets(user_id=1, name="Fridge", description="5 star",
                     price="Rs.14989",item=restaurant2)

session.add(menuItem1)
session.commit()

menuItem2 = Gadgets(user_id=1, name="Air Conditioner",
                     description="Good power", price="Rs.32000",item=restaurant2)

session.add(menuItem2)
session.commit()

menuItem3 = Gadgets(user_id=1, name="Mobile", description="All Features",
                     price="Rs.12000",item=restaurant2)

session.add(menuItem3)
session.commit()

menuItem4 = Gadgets(user_id=1, name="Television", description="Moreclarity ",
                     price="12",item=restaurant2)

session.add(menuItem4)
session.commit()

# Menu for Panda Garden
restaurant1 = Company(user_id=1, name="Panasonic")

session.add(restaurant1)
session.commit()


menuItem1 = Gadgets(user_id=1, name="Washing Machine", description="good quality",
                     price="Rs.15000",item=restaurant1)

session.add(menuItem1)
session.commit()

menuItem2 = Gadgets(user_id=1, name="Fridge", description="more efficent",
                     price="Rs.16987",item=restaurant1)

session.add(menuItem2)
session.commit()



# Menu for Thyme for that
restaurant1 = Company(user_id=1, name="Sony")

session.add(restaurant1)
session.commit()


menuItem1 = Gadgets(user_id=1, name="Mobile", description="good pixels",
                     price="Rs.9870",item=restaurant1)

session.add(menuItem1)
session.commit()


print "successfully added menu items!"
