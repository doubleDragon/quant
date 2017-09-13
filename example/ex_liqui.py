from config import settings
from liqui.client import PrivateClient as Client

client = Client(settings.LIQUI_API_KEY, settings.LIQUI_API_SECRET)

print(client.balance())
