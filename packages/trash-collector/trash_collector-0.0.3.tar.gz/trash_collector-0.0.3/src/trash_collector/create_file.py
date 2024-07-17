import random

CHUNK_SIZE = 1_024  # 1 kb

# 5mb
SIZE = 1_024 * 5  # * chunk_size

seed = "qwertyuıopasdfghjklizxcvbnm!'^+&/()=?-_|;"
seed_size = len(seed)


for _ in range(SIZE):
    l = ""
    for _ in range(CHUNK_SIZE):
        l += seed[int(random.random() * seed_size)]
    with open("testa.txt", "a") as f:
        f.write(l)
