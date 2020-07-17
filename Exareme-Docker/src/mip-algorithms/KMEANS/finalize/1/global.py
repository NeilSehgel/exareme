import sys

from KMEANS.kMeans import kMeans

def main(args):
    kMeans(args[1:]).global_final()

if __name__ == "__main__":
    kMeans(sys.argv[1:]).global_final()
