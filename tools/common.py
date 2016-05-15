import os
import io
import sys
import json
import argparse
import logging
import time
import threading
import queue
import string

logging.basicConfig(format='[%(levelname)s][%(asctime)s] %(message)s', level=logging.DEBUG)

def calculate_chars(text):
    char_sum = {}
    top_count = 0
    top_char = None
    for c in text:
        if c not in string.ascii_lowercase:
            continue
        if c in char_sum:
            char_sum[c] += 1
        else:
            char_sum[c] = 1
        if top_count < char_sum[c]:
            top_count = char_sum[c]
            top_char = c
    logging.info("[COMMON TOOL][CHAR CALCULATE] found top char {}, {} times".format(top_char, top_count))
    return top_char

def calculate_chars_with_group(text, group_size):
    text_list = []
    for i in range(0, group_size):
        text_list.append("")
    counter = 0
    for c in text:
        if c not in string.ascii_lowercase:
            continue
        text_list[counter] += c
        counter += 1
        counter %= group_size
    top_char_list = []
    for i in range(0, group_size):
        top_char_list.append(calculate_chars(text_list[i]))
    return top_char_list



