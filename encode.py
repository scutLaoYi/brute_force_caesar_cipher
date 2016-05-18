import os
import sys
import io
import logging
import string
import argparse
import tools.common


def generate_char_with_offset(origin_char, offset):
    offset %= tools.common.TOTAL_CHAR_IN_ALPHABET
    code = ord(origin_char) + offset
    if origin_char in string.ascii_lowercase:
        # overflow
        if code < ord('a'):
            code += tools.common.TOTAL_CHAR_IN_ALPHABET
        if code > ord('z'):
            code -= tools.common.TOTAL_CHAR_IN_ALPHABET
    elif origin_char in string.ascii_uppercase:
        if code < ord('A'):
            code += tools.common.TOTAL_CHAR_IN_ALPHABET
        if code > ord('Z'):
            code -= tools.common.TOTAL_CHAR_IN_ALPHABET
    else:
        #Not lower either upper, return initial
        return origin_char
    return chr(code)

def encode_with_caesar(plain_text, offset, total = -1):
    cipher_text = ""
    just_part = False
    if total > 0:
        just_part = True

    for t in plain_text:
        # ignore all other text
        if not t in string.ascii_letters:
            cipher_text += t
            continue
        # translate into character
        out = generate_char_with_offset(t, offset)
        cipher_text += out
        logging.debug("initial {} to {} with offset {}".format(t, out, offset))

        if just_part:
            total -= 1
            if total <= 0:
                break
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

def build_vigenere_offset_list(cipher, direction):
    if direction > 0:
        direction = 1
    else :
        direction = -1
    logging.info("[ENCODE][VIGENERE] Cipher [{}] length [{}]".format(cipher, len(cipher)))
    offset_list = []
    for c in cipher:
        if not c in string.ascii_letters:
            logging.error("[VIGENERE_KEY_BUILD] cipher with no alphabet detected!")
        offset_list.append(direction * (ord(c) - ord('a')))
    return offset_list

def encode_with_vigenere(plain_text, cipher, direction = 1, total = -1):
    offset_list = build_vigenere_offset_list(cipher, direction)
    offset_list_size = len(offset_list)
    if offset_list_size == 0:
        logging.error("[ENCODE][VIGENERE] cipher length zero!")
        return ""
    cipher_text = ""
    text_counter = 0
    just_part = False
    if total > 0:
        just_part = True
    for t in plain_text:
        if not t in string.ascii_letters:
            cipher_text += t
            continue
        cur_index_for_offset_list = text_counter % offset_list_size
        out = generate_char_with_offset(t, offset_list[cur_index_for_offset_list])
        cipher_text += out
        text_counter += 1
        logging.debug("[ENCODE][VIGENERE] initial {} to {} with offset {}".format(t, out, offset_list[cur_index_for_offset_list]))
        if just_part:
            total -= 1
            if total <= 0:
                break
    return cipher_text

def encrypt_file_with_vigenere(in_file, out_file, cipher, encrypt = 1):
    logging.info("[ENCODE][VIGENERE] Encrypt file [{}] with cipher [{}] into file [{}]".format(
        in_file,
        cipher,
        out_file)
        )
    output_file = open(out_file, 'w')
    with open(in_file) as f:
        text = f.read()
        cipher_text = encode_with_vigenere(text, cipher, encrypt)
        output_file.write(cipher_text)
    output_file.close()

def generate_with_formula(t, a, b):
    x = 0
    if t in string.ascii_lowercase:
        x = ord(t) - ord('a')
    else:
        x = ord(t) - ord('A')
    y = (a*x + b) % tools.common.TOTAL_CHAR_IN_ALPHABET
    if t in string.ascii_lowercase:
        return chr(y+ord('a'))
    else:
        return chr(y+ord('A'))


def encode_with_affine(plain_text, a, b, direction = 1):
    cipher_map = {}
    revert_map = {}
    for c in string.ascii_letters:
        _c = generate_with_formula(c, a, b)
        cipher_map[c] = _c
        revert_map[_c] = c

    cipher_text = ""
    for t in plain_text:
        if not t in string.ascii_letters:
            cipher_text += t
            continue
        if direction > 0:
            cipher_text += cipher_map[t]
        else :
            cipher_text += revert_map[t]
    return cipher_text

def encrypt_file_with_affine(in_file, out_file, a, b, direction):
    output_file = open(out_file, 'w')
    with open(in_file) as f:
        text = f.read()
        cipher_text = encode_with_affine(text, a, b, direction)
        output_file.write(cipher_text)
    output_file.close()

def test_caesar():
    logging.info("[ENCODE][TEST][CAESAR]Start")
    encrypt_file_with_caesar("plain_text.txt", "encrypt_caesar.txt", 5)

def test_decrypt_caesar():
    logging.info("[ENCODE][TEST][CAESAR DECRYPT]Start")
    encrypt_file_with_caesar("encrypt_caesar.txt", "decrypt_caesar.txt", -1)

def test_vigenere():
    logging.info("[ENCODE][TEST][VIGENERE]Start")
    encrypt_file_with_vigenere("plain_text.txt", "encrypt_vigenere.txt", "fuck")

def test_decrypt_vigenere():
    logging.info("[ENCODE][TEST][CAESAR DECRYPT]Start")
    encrypt_file_with_vigenere("encrypt_vigenere.txt", "decrypt_vigenere.txt", "bbbc", -1)

def test_affine():
    logging.info("[ENCODE][TEST][AFFINE]Start")
    encrypt_file_with_affine("plain_text.txt", "encrypt_affine.txt", 11, 5, 1)

def test_decode_affine():
    logging.info("[ENCODE][TEST][AFFINE DECRYPT]Start")
    encrypt_file_with_affine("encrypt_affine.txt", "decrypt_affine.txt", 11, 5, -1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-in', '--in_file', help='input file to be encrypt', type=str)
    parser.add_argument('-out', '--out_file', help='output file to store result', type=str)
    parser.add_argument('-type', '--encrypt_type', help='encrypt type config, 1 as caesar, 2 as vigenere', type=int)
    parser.add_argument('-key', '--encrypt_key', help='vigenere encrypt key setting', type=str)
    parser.add_argument('-offset', '--encrypt_offset', help='caesar encrypt offset setting', type=int)

    args = parser.parse_args()
    logging.info('[ENCODER] Encode file {} with type {} into file {}'.format(args.in_file, args.encrypt_type, args.out_file))
    if args.encrypt_type == 1:
        if not args.encrypt_offset :
            logging.error('[ENCODER] Encode with caesar needs offset setting!')
            return
        else :
            logging.info('[ENCODER] Caesar with offset {}'.format(args.encrypt_offset))
            encrypt_file_with_caesar(args.in_file, args.out_file, args.encrypt_offset)
    elif args.encrypt_type == 2:
        if not args.encrypt_key:
            logging.error('[ENCODER] Encode with vigenere needs key setting!')
            return
        else :
            logging.info('[ENCODER] vigenere with key {}'.format(args.encrypt_key))
            encrypt_file_with_vigenere(args.in_file, args.out_file, args.encrypt_key)
    logging.info('[ENCODER] Output into file:{}'.format(args.out_file))
    return

if __name__ == "__main__":
    test_decode_affine()





