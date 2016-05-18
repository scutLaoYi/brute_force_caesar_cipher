import tools.common
import threading
import time
import logging
import encode
import spell_check
import queue
import argparse
import string

#TOP_CHAR_IN_ENGLISH = "etaoinsrh"
TOP_CHAR_IN_ENGLISH = "etao"
g_cipher_text = ""
g_plain_text = ""

g_working_queue = None
spell_checker = None
args = None

class CrackJob:
    def __init__(self, offset=0, key="", _type=1, a=0, b=0):
        self.type = _type
        self.offset = offset
        self.key = key
        self.a = a
        self.b = b

class CrackThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.threadID = id
        logging.info('[CRACKER] Thread start with id {}'.format(id))
    def run(self):
        global g_working_queue
        global g_plain_text
        while not g_working_queue.empty():
            job = g_working_queue.get()
            if job.type == 2:
                logging.info('[CRACKER] ID:{} Type:vigenere Key:{}'.format(self.threadID, job.key))

                if (spell_checker.score(encode.encode_with_vigenere(g_cipher_text, job.key, -1, 100)) < 30):
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} failed in pre crack, ignore!'.format(self.threadID, job.key))
                    continue

                plain_text = encode.encode_with_vigenere(g_cipher_text, job.key, -1)
                score = spell_checker.score(plain_text)
                if (score > 90):
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Success Score:{}'.format(self.threadID, job.key, score))
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Failed Score:{}'.format(self.threadID, job.key, score))
            elif job.type == 1:
                logging.info('[CRACKER] ID:{} Type:caesar offset:{}'.format(self.threadID, job.offset))
                if (spell_checker.score(encode.encode_with_caesar(g_cipher_text, job.offset, 100)) < 30):
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} failed in pre crack, ignore!'.format(self.threadID, job.offset))
                    continue

                plain_text = encode.encode_with_caesar(g_cipher_text, job.offset)
                score = spell_checker.score(plain_text)
                if (score > 90):
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Success Score:{}'.format(self.threadID, job.offset, score))
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Failed Score:{}'.format(self.threadID, job.offset, score))
            elif job.type == 3:
                logging.info('[CRACKER] ID:{} Type:affine a:{} b:{}'.format(self.threadID, job.a, job.b))
                if (spell_checker.score(encode.encode_with_affine(g_cipher_text, job.a, job.b, -1, 100)) < 30):
                    logging.info('[CRACKER] ID:{} Type:affine a:{} b:{} failed in pre crack, ignore'.format(self.threadID, job.a, job.b))
                    continue
                plain_text = encode.encode_with_affine(g_cipher_text, job.a, job.b, -1)
                score = spell_checker.score(plain_text)
                if (score > 90):
                    logging.info('[CRACKER] ID:{} Type:affine a:{} b:{} Result:Success Score:{}'.format(self.threadID, job.a, job.b, score))
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:affine a:{} b:{} Result:Failed, Score:{}'.format(self.threadID, job.a, job.b, score))
            else:
                logging.error('[CRACKER] type error, ignore')

def prepare_crack_with_caesar():
    if (len(g_cipher_text) == 0):
        logging.error("[CRACKER][CAESAR] Empty cipher text! exit!")
        return
    top_char = tools.common.calculate_chars(g_cipher_text)
    for tc in TOP_CHAR_IN_ENGLISH:
        offset = ord(tc) - ord(top_char)
        job = CrackJob(offset=offset, _type=1)
        g_working_queue.put(job)
        logging.debug("[CRACKER][CAESAR] Add a job with offset {}".format(offset))
    return

def prepare_crack_with_vigenere(key_length):
    if (len(g_cipher_text) == 0):
        logging.error("[CRACKER][VIGENERE] Empty cipher text! exit!")
        return
    top_char_list = tools.common.calculate_chars_with_group(g_cipher_text, key_length)
    def build_key(depth, key_part):
        if (depth == key_length):
            job = CrackJob(key=key_part, _type=2)
            g_working_queue.put(job)
            logging.debug("[CRACKER][VIGENERE] Add a job with key {}".format(key_part))
            return
        top_char = top_char_list[depth]
        for tc in TOP_CHAR_IN_ENGLISH:
            offset = ord(top_char) - ord(tc)
            if offset < 0:
                offset += tools.common.TOTAL_CHAR_IN_ALPHABET
            cur_key_char = chr(ord('a') + offset)
            build_key(depth+1, key_part+cur_key_char)
    build_key(0, "")

def prepare_crack_with_affine():
    if (len(g_cipher_text) == 0):
        logging.error("[CRACKER][CAESAR] Empty cipher text! exit!")
        return
    top_char = tools.common.calculate_chars(g_cipher_text)
    top_char = top_char.lower()
    top_offset = ord(top_char) - ord('a')

    for p in TOP_CHAR_IN_ENGLISH:
        for a in tools.common.POSSIBLE_A_IN_AFFINE:
            for b in range(0, 26):
                if top_char == encode.generate_with_formula(p, a, b):
                    job = CrackJob(_type=3, a=a, b=b)
                    g_working_queue.put(job)
                    logging.debug("[CRACKER][AFFINE] Add a job with a:{}, b:{}".format(a, b))
    return

def calculate_vigenere_key_length():
    pure_text = ""
    for c in g_cipher_text:
        if c not in string.ascii_letters:
            continue
        pure_text += c.lower()

    text_length = len(pure_text)
    match_map = {}
    max_match_length = 1
    max_match_amount = 0
    MAXIMUM_KEY_LENGTH = 50
    total_match_sum = 0
    for i in range(0, text_length):
        for move in range(1, MAXIMUM_KEY_LENGTH+1):
            target = i - move
            if target < 0:
                target += text_length
            if pure_text[i] == pure_text[target]:
                if move in match_map:
                    match_map[move] += 1
                else:
                    match_map[move] = 1
                total_match_sum += 1
    average_match = total_match_sum / MAXIMUM_KEY_LENGTH
    for i in range(1, MAXIMUM_KEY_LENGTH+1):
        #This is a parameter
        if (match_map[i] - average_match) / average_match > 0.3:
            max_match_length = i
            max_match_amount = match_map[i]
            break

    print("key length:{}, match:{}".format(max_match_length, max_match_amount))
    return max_match_length

def crack_file(in_file, out_file):
    with open(in_file) as f:
        global g_cipher_text
        g_cipher_text = f.read()
    ts_start = time.time()
    if args.encrypt_type == 1:
        prepare_crack_with_caesar()
    elif args.encrypt_type == 2:
        key_length = calculate_vigenere_key_length()
        prepare_crack_with_vigenere(key_length)
    elif args.encrypt_type == 3:
        prepare_crack_with_affine()

    for i in range(0, args.threads):
        thread = CrackThread(i)
        thread.start()
    while(threading.activeCount() > 1):
        time.sleep(1)
    if (len(g_plain_text) > 0):
        ts_end = time.time()
        logging.info("[CRACK][MAIN] Success!Time used:{}".format(ts_end-ts_start))
        with open(out_file, 'w') as f:
            f.write(g_plain_text)
    else :
        logging.info("[CRACK][MAIN] Failed!")


def main():
    logging.info("[main] Engine Start!")
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threads', help='thread to crack', type = int)
    parser.add_argument('-in', '--in_file', help='input file to be crack', type=str)
    parser.add_argument('-out', '--out_file', help='output file to store result', type=str)
    parser.add_argument('-dic', '--dictionary', help='dictionary file to check whether crack is success', type=str)
    parser.add_argument('-type', '--encrypt_type', help='encrypt type config, 1 as caesar, 2 as vigenere, 3 as affine', type=int)
    #parser.add_argument('-l', '--key_length', help='key length setting for vigenere crack', type=int)
    global args
    args = parser.parse_args()
    logging.info('[main] try to crack file:{}, with type {}, store into file:{}'.format(args.in_file, args.encrypt_type, args.out_file))
    if args.encrypt_type == 2 and not args.key_length:
        logging.error('[main] Error: vigenere encrypt needs key length setting to crack')
        return

    global spell_checker
    spell_checker = spell_check.SpellChecker(args.dictionary)
    global g_working_queue
    g_working_queue = queue.Queue()

    crack_file(args.in_file, args.out_file)
    logging.info("[main] Exit!")
    return

if __name__ == "__main__":
    main()
