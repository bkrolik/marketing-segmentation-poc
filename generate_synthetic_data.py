"""
Helpers for generating synthetic resident data for seeding and testing.

Provides `generate_residents` to create a list of synthetic resident tuples.
"""

import random
import string


def generate_residents(n=5000):
    """
    Generate synthetic resident records.

    Args:
        n (int): Number of resident records to generate (default 5000).

    Returns:
        list[tuple]: Rows of `(pid, age, income, kids, distance)`.
    """

    residents = []
    for _ in range(n):
        pid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        age = random.randint(1, 90)
        income = random.choice([30000, 50000, 75000, 100000, 150000])
        kids = random.choice([True, False])
        distance = round(random.uniform(0.1, 10.0), 2)
        residents.append((pid, age, income, kids, distance))
    return residents


if __name__ == "__main__":
    data = generate_residents(5000)
    print("INSERT INTO residents.resident_core VALUES")
    for row in data:
        print(f"('{row[0]}', {row[1]}, {row[2]}, {str(row[3]).lower()}, {row[4]}),")
