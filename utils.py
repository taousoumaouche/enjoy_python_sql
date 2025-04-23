from email_validator import validate_email, EmailNotValidError
import phonenumbers
import userDB
from random import randint
from password_validator import PasswordValidator

schema = PasswordValidator()
schema\
.min(8)\
.max(100)\
.has().uppercase()\
.has().lowercase()\
.has().digits()\
.has().no().spaces()\

def isValidEmail(email):
    try:
        # Check that the email address is valid. Turn on check_deliverability
        # for first-time validations like on account creation pages (but not
        # login pages).
        emailinfo = validate_email(email, check_deliverability=False)

        # After this point, use only the normalized form of the email address,
        # especially before going to a database query.
        email = emailinfo.normalized

        return email

    except EmailNotValidError as e:

        return False

def isValidNumber(numero):
    numeroinfo = phonenumbers.parse(numero,"FR")
    if phonenumbers.is_valid_number(numeroinfo):
        return numero
    else:
        return False
    
def isValidPassword(Password):
    return schema.validate(str(Password))

def isValidCodePostal(Code):
    return len(Code) == 5

def genererMatricule():
    return randint(100000,999999)

def decode_photo(photo_bytea):
    if photo_bytea is None:
        return None
    # 1. .hex() : Transforme les données binaires en chaîne hexadécimale.
    # 2. bytes.fromhex() : Reconvertit la chaîne hexadécimale en données binaires.
    # 3. .decode('utf-8') : Décode les données binaires en une chaîne UTF-8 lisible.
    return bytes.fromhex(photo_bytea.hex()).decode('utf-8')
