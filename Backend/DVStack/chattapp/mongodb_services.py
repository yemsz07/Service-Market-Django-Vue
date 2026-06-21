from pymongo import MongoClient

# Siguraduhin na ang string ay walang putol at nasa loob ng double quotes
MONGO_URI = "mongodb+srv://yemsz07_db_user:qwerty123@cluster0.85vsamp.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client['ecommerce_chat_db']