from os import getenv

from dotenv import load_dotenv

from project.databases import Database

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
DB_NAME = getenv("DB_NAME")

db = Database(DB_NAME)