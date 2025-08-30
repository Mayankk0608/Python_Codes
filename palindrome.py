def palindrome(n):
    num = str(n)
    reverse = num[::-1]  # [::-1] is used to create a reverse copy of the string 

    return num == reverse

print(f"Is 121 a palindrome? {palindrome(121)}")
print(f"Is 12345 a palindrome? {palindrome(12345)}")
print(f"Is -121 a palindrome? {palindrome(-121)}")
print(f"Is 0 a palindrome? {palindrome(0)}")

