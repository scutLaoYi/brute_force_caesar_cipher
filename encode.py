import os
import sys
import io
import logging
import string

def encode_with_caesar(plain_text, offset):
    cipher_text = ""
    for t in plain_text:
        # ignore all other text
        if not t in string.ascii_lowercase:
            cipher_text += t
            continue
        # move in ascii with offset
        code = ord(t) + offset
        # move back if overflow
        if code > ord('z'):
            code -= 26
        # translate into character
        char = chr(code)
        cipher_text += char
    return cipher_text

def encrypt_file_with_caesar(in_file, out_file, offset):
    output_file = open(out_file, 'w')
    with open(in_file) as f:
        for line in f:
            cipher_text = encode_with_caesar(line, offset)
            output_file.write(cipher_text)
    output_file.close()


def test():
    encrypt_file_with_caesar("plain_text.txt", "encrypt_caesar.txt", 2)

def main():
    test()

if __name__ == "__main__":
    main()





