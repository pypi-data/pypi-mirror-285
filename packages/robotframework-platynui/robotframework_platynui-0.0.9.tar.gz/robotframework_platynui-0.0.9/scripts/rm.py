import os
import shutil
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rm.py <file>")
        sys.exit(1)

    for i in range(1, len(sys.argv)):
        if not os.path.exists(sys.argv[i]):
            print("File", sys.argv[i], "does not exist")
            continue
        try:
            shutil.rmtree(sys.argv[i])
        except BaseException:
            try:
                os.remove(sys.argv[i])
            except BaseException:
                print("Failed to remove", sys.argv[i])
                sys.exit(1)
