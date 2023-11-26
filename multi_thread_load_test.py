# from concurrent.futures import ThreadPoolExecutor

# import requests

# from timer import timer

# URL = 'https://flask-api-405922.ew.r.appspot.com/test/0x7b901f40228fc5ca87a288a7c1e88bc439741fcf'


# def fetch(session, url):
#     with session.get(url) as response:
#         print(response.json())


# @timer(1, 5)
# def main():
#     with ThreadPoolExecutor(max_workers=50) as executor:
#         with requests.Session() as session:
#             executor.map(fetch, [session] * 50, [URL] * 50)
#             executor.shutdown(wait=True)