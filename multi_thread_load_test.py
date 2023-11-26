# from concurrent.futures import ThreadPoolExecutor

# import requests

# from timer import timer

# URL = 'https://flask-api-405922.ew.r.appspot.com/transactions/'
# myobj = {'address': '0x7b901f40228fc5ca87a288a7c1e88bc439741fcf'}


# def post_request(session, url, obj):
#     response = session.post(url, json=obj)
#     print(response.json())

# @timer(1, 5)
# def main():
#     with ThreadPoolExecutor(max_workers=75) as executor:
#         with requests.Session() as session:
#             executor.map(post_request, [session] * 75, [URL] * 75, [myobj] * 75)
#             executor.shutdown(wait=True)
