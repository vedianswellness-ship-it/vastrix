import os

# 1. Create the .streamlit folder if it doesn't exist
folder_name = ".streamlit"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print("Created folder: .streamlit")
else:
    print(".streamlit folder already exists.")

# 2. Write the credentials into the secrets.toml file
secrets_content = """[mongo]
connection_string = "mongodb+srv://your_username:your_password@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority"
"""

file_path = os.path.join(folder_name, "secrets.toml")
with open(file_path, "w") as f:
    f.write(secrets_content)

print("Created and wrote to: .streamlit/secrets.toml")
print("Please replace 'your_username' and 'your_password' inside the file with your actual MongoDB credentials now!")
