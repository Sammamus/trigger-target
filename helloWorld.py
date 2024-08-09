import sys
import time

# Global
sleep_timer = 600


def sleeper():
    print("Sleeping")
    time.sleep(sleep_timer)
    print("Done")


def main(name):
    try:
        print(f"Hello {name}!")
        time.sleep(sleep_timer)
        exit(0)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    arg = sys.argv[1]
    main(arg)