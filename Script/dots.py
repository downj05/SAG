import json
import time

def increment_email_counter(email):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {'emails': {}}

    # Create the emails dict if it doesn't exist
    if 'emails' not in data:
        data['emails'] = {}

    if email not in data['emails']:
        data['emails'][email] = {'count': 0, 'last_update': time.time()}

    data['emails'][email]['count'] += 1
    data['emails'][email]['last_update'] = time.time()

    with open('counter.json', 'w') as f:
        json.dump(data, f)

    return data['emails'][email]['count']

def get_email_counter(email):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return 0

    return data['emails'].get(email, {'count': 0})['count']

def get_email_last_update(email):
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return 0

    return data['emails'].get(email, {'last_update': 0})['last_update']

def email_combination(email: str, index: int):
    head, domain = email.split("@")
    comb = _binary_representation(head, index)

    return f"{comb}@{domain}"

def estimateDotCombination(email: str) -> int:
    """
    Estimate the number of dot combinations for a given email address.
    """
    username = email.split("@")[0]  # get the part of the email before the '@'
    return 2 ** max(0, len(username) - 3)  # calculate the number of combinations

def _binary_representation(s: str, i: int) -> str:
    binary = bin(i)[2:].zfill(len(s) - 1)
    result = s[0]
    for char, bit in zip(s[1:], binary):
        if bit == '1':
            result += '.' + char
        else:
            result += char
    return result

if __name__ == "__main__":
    e = 'heyheywerethemonkeys443@gmail.com'
    emails = []
    for i in range(estimateDotCombination(e)):
        email_combination(e, i)