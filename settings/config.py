from dotenv import load_dotenv
import os

load_dotenv()

test = 'qqwe'

BOT_TOKEN  = os.getenv('BOT_TOKEN')

db_host = os.getenv('db_host')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')
api_key_google = os.getenv('api_key_google')
admin_id = int(os.getenv('admin_id'))
