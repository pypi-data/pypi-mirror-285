from Crypto import Random
from Crypto.Cipher import AES
import os


def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

# rellenamos con * para que la contrasena pueda tener 32 bytes
# en caso de ser menor a los 32 bytes
# y determinamos el typo de la data

def typeKey(data):
    if(type(data) is str):
        data = bytes(("*"*(32-len(data)) + data).encode("utf-8"))
    
    if(type(data) is bytes):
        data = b"*"*(32-len(data)) + data
    
    return data

def typeData(data):

    if(type(data) is str):
        data = bytes(data.encode("utf-8"))
    
    return data

def encrypt(message, key, key_size=256):
    key = typeKey(key)
    message = pad(typeData(message))
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    # rellenamos con * para que la contrasena pueda tener 32 bytes
    key = typeKey(key)
    ciphertext = typeData(ciphertext)
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])

    return plaintext.rstrip(b"\0")


def encrypt_file(file_name,key):
    try:
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = encrypt(plaintext, key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_name)
        return file_name + ".enc"
    except Exception as e:
        print(e)

def decrypt_file(file_name,key):
    try:
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = decrypt(ciphertext, key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        os.remove(file_name)
    except Exception as e:
        print(e)





