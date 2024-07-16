import random

def lotto():
    recommand_lotto_numbers = random.sample(range(1,46),6)
    recommand_lotto_numbers.sort();
    print(*recommand_lotto_numbers)
