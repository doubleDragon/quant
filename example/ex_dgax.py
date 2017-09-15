#!/usr/bin/python
# -*- coding: UTF-8 -*-


from gdax.public_client import PublicClient as Client

client = Client()
print(client.get_products())


