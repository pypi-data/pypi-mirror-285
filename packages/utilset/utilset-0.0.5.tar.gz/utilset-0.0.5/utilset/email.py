import re

pattern = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"

def is_valid(email):
    if re.search(pattern, email):
        return True
    else:
        return False
    
def get_domain(email):
    arr = email.split('@')
    return arr[1].lower()