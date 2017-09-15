import re
value='aaa'
# pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
pattern = re.compile(r'^[\d\w\.]+$')
print pattern.match(value)