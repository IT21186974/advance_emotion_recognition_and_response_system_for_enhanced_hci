from auth import authenticate_user

username = input("Username: ")
password = input("Password: ")

if authenticate_user(username, password):
    print("Authentication successful")
else:
    print("Authentication failed")
