""" Tool to build a key pass for xAAL config file"""

from xaal.lib import tools
import binascii

def main():
    try:
        temp = input("Please enter your passphrase: ")
        key  = tools.pass2key(temp)
        print("Cut & Paste this key in your xAAL config-file")
        print("key=%s"% binascii.hexlify(key).decode('utf-8'))
    except KeyboardInterrupt:
        print("Bye Bye..")
        

if __name__ == '__main__':
    main()
