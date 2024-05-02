from sqlalchemy import Column, Integer, Boolean, DateTime


# Define model
class BaseModel:
    """
    Base model for a database table
    """
    id = Column(Integer, primary_key=True, index=True)
    is_deleted = Column(Boolean, default=False)
    created_date = Column(DateTime)
    last_modified_date = Column(DateTime)
