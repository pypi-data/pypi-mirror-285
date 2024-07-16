from xaal.lib import tools
import sys


def main():
    uuid = None
    if len(sys.argv) > 1:
        value = sys.argv[1]
        uuid = tools.get_uuid(value)
    if uuid == None:
        uuid=tools.get_random_uuid()
    print("TXT: %s" % uuid)

    print("HEX: ",end="")
    for b in uuid.bytes:
        print("0x%x" % b,end=',')
    print()

    print("INT: ",end="")
    for b in uuid.bytes:
        print("%d" % b,end=',')
    print()

if __name__ == '__main__':
    main()
