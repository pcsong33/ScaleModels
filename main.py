from random import randint
from time import sleep

def main():
    clock_rate = randint(1, 6)

    # listen to other processes:
    while True:
        # sleep according to clock rate
        sleep(1/clock_rate)


if __name__ == '__main__':
    main()

