from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

class CategoryType(Enum):
    PRODUCT = 'product'
    POST = 'post'
    BOTH = 'both'