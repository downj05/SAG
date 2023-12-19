import argparse

parser = argparse.ArgumentParser(
    description="Generate dot combinations for an email, preferably a gmail address",
    usage="python dots.py <email>",
)
parser.add_argument("email", help="Email to generate dot combinations for")

args = parser.parse_args()


def email_combinations(email):
    head, domain = email.split("@")
    combs = generate_dot_combinations(head)
    for c in combs:
        print(f"{c}@{domain}")


def generate_dot_combinations(s):
    """
    Generate all possible combinations of dots in-between the characters of a given string.

    Args:
        s (str): The input string.

    Returns:
        list: A list of all possible dot combinations.
    """
    # Base case: if the string has length 1 or 2, return it unmodified
    if len(s) < 3:
        return [s]

    # Recursive case: insert a dot after the first character, and generate
    # all possible combinations of dots for the remainder of the string
    dot_combinations = []
    for i in range(1, len(s) - 1):
        for combination in generate_dot_combinations(s[i:]):
            dot_combinations.append(s[:i] + "." + combination)

    # Return the list of dot combinations
    return dot_combinations


if __name__ == "__main__":
    email_combinations(args.email)
