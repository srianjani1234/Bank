# s = "1234"
# s1 = ''
# for i in s:
#     s1+=chr(int(i))
# print(s1)
# s = "1234"
# s2 = ''
# for i in s1:
#     s2+=str(ord(i))
# print(s2)

# s = "6066"
# s2 = ''
# for i in s:
#     s2 +=chr(int(i))
# print(s2)

# if s1 == s2:
#     print("successfully wasted 80 days")
# else:
#     print("another method")

# #####
# s3 = "1234"
# s4 = ''
# for i in s3:
#     s4 +=chr(int(i))

# print(s4)
# if s1 == s4:
#     print("successfully wasted 80 days")
# else:
#     print("another method")
# print(s1)


import  hashlib 
a = hashlib.sha1("Admin@123".encode())
print(a.digest())
