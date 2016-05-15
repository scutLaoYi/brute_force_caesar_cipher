import tools.common
import threading
import time
import logging
import encode
import spell_check
import queue
import argparse

TOP_CHAR_IN_ENGLISH = "etaoinsrh"
#TOP_CHAR_IN_ENGLISH = "etaoi"
g_cipher_text = ""
g_plain_text = ""

g_working_queue = None
spell_checker = None
args = None

class CrackJob:
    def __init__(self, offset, key):
        self.offset = offset
        self.key = key

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
            if (len(job.key) > 0):
                logging.info('[CRACKER] ID:{} Type:vigenere Key:{}'.format(self.threadID, job.key))
                plain_text = encode.encode_with_vigenere(g_cipher_text, job.key, -1)
                score = spell_checker.score(plain_text)
                if (score > 90):
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Success Score:{}'.format(self.threadID, job.key, score))
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Failed Score:{}'.format(self.threadID, job.key, score))
            else:
                logging.info('[CRACKER] ID:{} Type:caesar offset:{}'.format(self.threadID, job.offset))
                plain_text = encode.encode_with_caesar(g_cipher_text, job.offset)
                score = spell_checker.score(plain_text)
                if (score > 90):
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Success Score:{}'.format(self.threadID, job.offset, score))
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Failed Score:{}'.format(self.threadID, job.offset, score))


def prepare_crack_with_caesar():
    if (len(g_cipher_text) == 0):
        logging.error("[CRACKER][CAESAR] Empty cipher text! exit!")
        return
    top_char = tools.common.calculate_chars(g_cipher_text)
    for tc in TOP_CHAR_IN_ENGLISH:
        offset = ord(tc) - ord(top_char)
        job = CrackJob(offset, "")
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
            job = CrackJob(0, key_part)
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

def crack_file(in_file, out_file):
    with open(in_file) as f:
        global g_cipher_text
        g_cipher_text = f.read()
    if args.encrypt_type == 1:
        prepare_crack_with_caesar()
    else :
        prepare_crack_with_vigenere(args.key_length)
    for i in range(0, args.threads):
        thread = CrackThread(i)
        thread.start()
    while(threading.activeCount() > 1):
        time.sleep(1)
    if (len(g_plain_text) > 0):
        logging.info("[CRACK][MAIN] Success!")
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
    parser.add_argument('-type', '--encrypt_type', help='encrypt type config, 1 as caesar, 2 as vigenere', type=int)
    parser.add_argument('-l', '--key_length', help='key length setting for vigenere crack', type=int)
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
