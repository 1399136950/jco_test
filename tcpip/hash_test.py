import hashlib

a1=hashlib.md5()
a2=hashlib.md5()
a3=hashlib.md5()
user, passwd= 'user', 'user'
realm='jconvs'
nonce='2316d25fb521db2dc1cab985b38b3071'
uri="rtsp://192.168.150.45:554/stream2"
public_method = 'DESCRIBE'

str1='{}:{}:{}'.format(user,realm,passwd).encode()
a1.update(str1)
str1=a1.hexdigest()

str2='{}:{}'.format(public_method,uri).encode()
a2.update(str2)
str2=a2.hexdigest()

str3='{}:{}:{}'.format(str1,nonce,str2).encode()
a3.update(str3)
str3=a3.hexdigest()
