import sys
from station import set_up
from commun import set_url

if __name__ == "__main__":
    name = None
    url = None
    print(sys.argv, len(sys.argv))
    if len(sys.argv) > 3:
        print("Usage: python main.py [name] [URL]")
        sys.exit(1)
    if len(sys.argv) > 1:
        name = sys.argv[1]
    if len(sys.argv) > 2:
        url = sys.argv[2]
    name = input("Enter your name: ") if name is None else name
    if url: set_url(url)
    set_up(name)
