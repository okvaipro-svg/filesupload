import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://corndb:cornbotdb@cluster0.qkaprkc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

BOT_TOKENS = [
    os.getenv("BOT_TOKEN_1", "7727808398:AAE2o8UtxsSYhYUTJWePOni0jXZWo4ipVew"),
    os.getenv("BOT_TOKEN_2", "8298170893:AAGEncRQjGsWzpulLn_27J7moxtSJ1K2avc"),
    os.getenv("BOT_TOKEN_3", "8406916310:AAFKNaFmeYholPCkA2dXiQgnfI8p6WvldKU")
]

SAVED_CHANNEL_ID = int(os.getenv("SAVED_CHANNEL_ID", "-1003133705295"))
MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID", "-1003132582396"))
LOGGER_CHANNEL_ID = int(os.getenv("LOGGER_CHANNEL_ID", "-1003183652455"))

OWNER_ID = int(os.getenv("OWNER_ID", "7924074157"))
SUDO_ID = int(os.getenv("SUDO_ID", "5294360309"))

BOT_REQUIRED_CHANNELS = {
    1: [
        "DataTraceUpdates",
        "+tON4QbKGs5k4NjBl",
        "+pVVo-sk9GwA1YzJl",
        "+GotefTYEgXxkNjY1"
    ],
    2: [
        "+6OTUDuSqJTE2ZjU1",
        "+sZ_HvIX7pMFkOGY1",
        "+U3OS5wDPoqRjOTY1",
        "+GotefTYEgXxkNjY1"
    ],
    3: [
        "+63BtI7See3swNTk1",
        "+iedooNdK0JQ1YTA1",
        "AakashPosts",
        "+GotefTYEgXxkNjY1"
    ]
}

POST_TIME_HOUR = int(os.getenv("POST_TIME_HOUR", "10"))
POST_TIME_MINUTE = int(os.getenv("POST_TIME_MINUTE", "0"))

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
