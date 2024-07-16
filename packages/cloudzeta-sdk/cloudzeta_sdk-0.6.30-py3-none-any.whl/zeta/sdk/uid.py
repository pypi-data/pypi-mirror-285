import random
import time

def generate_uid() -> str:
    length = 16
    # Characters that are safe and URL-friendly
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    n: int = int(time.time() * 1000)
    arr = []
    while n:
        n, rem = divmod(n, 36)
        arr.append(chars[rem])
    arr.reverse()
    timestamp = "".join(arr)

    random_part = ""
    random_part_length = length - len(timestamp)
    for i in range(random_part_length):
        random_index = random.randint(0, len(chars) - 1)
        random_part += chars[random_index]

    return timestamp + random_part


if __name__ == "__main__":
    print(generate_uid())