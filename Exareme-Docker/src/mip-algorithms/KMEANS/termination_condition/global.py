import sys

from KMEANS.kMeans import kMeans

def main(args):
    kMeans(args[1:]).termination_condition()

if __name__ == "__main__":
    kMeans(sys.argv[1:]).termination_condition()
