import os
import sys
import io
import logging
import string
logging.basicConfig(format='[%(levelname)s][%(asctime)s] %(message)s', level=logging.DEBUG)

def generate_char_with_offset(origin_char, offset):
    code = ord(origin_char) + offset
    # overflow
    if code < ord('a'):
        code += 26
    if code > ord('z'):
        code -= 26
    return chr(code)

def encode_with_caesar(plain_text, offset):
    cipher_text = ""
    for t in plain_text:
        # ignore all other text
        if not t in string.ascii_lowercase:
            cipher_text += t
            continue
        # translate into character
        out = generate_char_with_offset(t, offset)
        cipher_text += out
        logging.debug("initial {} to {} with offset {}".format(t, out, offset))
    return cipher_text

def encrypt_file_with_caesar(in_file, out_file, offset):
    logging.info("[ENCODE][CAESAR] Encrypt file [{}] with offset [{}] into file [{}]".format(
        in_file,
        offset,
        out_file)
        )
    output_file = open(out_file, 'w')
    with open(in_file) as f:
        text = f.read()
        cipher_text = encode_with_caesar(text, offset)
        output_file.write(cipher_text)
    output_file.close()

def build_vigenere_offset_list(cipher):
    logging.info("[ENCODE][VIGENERE] Cipher [{}] length [{}]".format(cipher, len(cipher)))
    offset_list = []
    for c in cipher:
        if not c in string.ascii_lowercase:
            logging.error("[VIGENERE_KEY_BUILD] cipher with no alphabet detected!")
        offset_list.append(ord(c) - ord('a'))
    return offset_list

def encode_with_vigenere(plain_text, cipher):
    offset_list = build_vigenere_offset_list(cipher)
    offset_list_size = len(offset_list)
    if offset_list_size == 0:
        logging.error("[ENCODE][VIGENERE] cipher length zero!")
        return ""
    cipher_text = ""
    text_counter = 0
    for t in plain_text:
        if not t in string.ascii_lowercase:
            cipher_text += t
            continue
        cur_index_for_offset_list = text_counter % offset_list_size
        out = generate_char_with_offset(t, offset_list[cur_index_for_offset_list])
        cipher_text += out
        text_counter += 1
        logging.debug("[ENCODE][VIGENERE] initial {} to {} with offset {}".format(t, out, offset_list[cur_index_for_offset_list]))
    return cipher_text

def encrypt_file_with_vigenere(in_file, out_file, cipher):
    logging.info("[ENCODE][VIGENERE] Encrypt file [{}] with cipher [{}] into file [{}]".format(
        in_file,
        cipher,
        out_file)
        )
    output_file = open(out_file, 'w')
    with open(in_file) as f:
        text = f.read()
        cipher_text = encode_with_vigenere(text, cipher)
        output_file.write(cipher_text)
    output_file.close()

def test_caesar():
    logging.info("[ENCODE][TEST][CAESAR]Start")
    encrypt_file_with_caesar("plain_text.txt", "encrypt_caesar.txt", 1)

def test_vigenere():
    encrypt_file_with_vigenere("plain_text.txt", "encrypt_vigenere.txt", "bbbc")

def main():
    test_vigenere()

if __name__ == "__main__":
    main()





