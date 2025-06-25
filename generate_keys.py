import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# Define users
names = ["Catarina Nunes", "Beatriz Monteiro", "Margarida Raposo", "Teresa Menezes"]
usernames = ["catarinagn", "bea_m", "magui", "teresa"]
passwords = ["abcd11", "cde22", "fgh33", "ijk44"]

# Use the correct method for v0.4.2
hashed_passwords = stauth.Hasher(["abcd11", "cde22", "fgh33", "ijk44"]).generate()

# Save hashed passwords to a file
file_path = Path("hashed_pw.pkl")
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
