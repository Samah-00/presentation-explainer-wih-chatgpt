from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
import os

# Get the directory path of the Python script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Verify if the 'db' folder exists
db_folder_path = os.path.join(script_directory, 'db')
db_file_path = os.path.join(db_folder_path, 'database.db')

# Create the 'db' folder if it doesn't exist
os.makedirs('db', exist_ok=True)

if os.path.exists(db_folder_path):
    # Create a database engine and session
    engine = create_engine(f'sqlite:///{db_file_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
else:
    raise FileNotFoundError(f"The database file '{db_file_path}' does not exist.")

# Define the database model
Base = declarative_base()


# Define the User and Upload classes as ORM models:
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    uploads = relationship("Upload", back_populates="user")


class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True)
    uid = Column(String, unique=True, nullable=False)
    filename = Column(String)
    upload_time = Column(DateTime)
    finish_time = Column(DateTime)
    status = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="uploads")


# Drop the existing tables if they exist
Base.metadata.drop_all(engine)

# Create the database tables if they don't exist
Base.metadata.create_all(engine)
