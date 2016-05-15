import tools.common
import threading
import time
import logging
import encode
import spell_check
import queue

TOP_CHAR_IN_ENGLISH = "etaoinsrh"
g_cipher_text = ""
g_plain_text = ""

g_working_queue = None
spell_checker = None

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
        while not g_working_queue.empty():
            job = g_working_queue.get()
            if (len(job.key) > 0):
                logging.info('[CRACKER] ID:{} Type:vigenere Key:{}'.format(self.threadID, job.key))
                plain_text = encode.encode_with_vigenere(g_cipher_text, job.key, -1)
                if (spell_checker.score(plain_text) > 90):
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Success'.format(self.threadID, job.key))
                    global g_plain_text
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:vigenere Key:{} Result:Failed'.format(self.threadID, job.key))
            else:
                logging.info('[CRACKER] ID:{} Type:caesar Key:{}'.format(self.threadID, job.key))
                plain_text = encode.encode_with_caesar(g_cipher_text, job.offset)
                if (spell_checker.score(plain_text) > 90):
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Success'.format(self.threadID, job.offset))
                    global g_plain_text
                    g_plain_text = plain_text
                    g_working_queue.queue.clear()
                else:
                    logging.info('[CRACKER] ID:{} Type:caesar offset:{} Result:Failed'.format(self.threadID, job.offset))


def prepare_crack_with_caesar():
    if (len(g_cipher_text) == 0):
        logging.error("[CRACKER][CAESAR] Empty cipher text! exit!")
        return
    top_char = tools.common.calculate_chars(g_cipher_text)
    for tc in TOP_CHAR_IN_ENGLISH:
        offset = ord(top_char) - ord(tc)
        job = CrackJob(offset, "")
        g_working_queue.put(job)
        logging.info("[CRACKER][CAESAR] Add a job with offset {}".format(offset))
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
            logging.info("[CRACKER][VIGENERE] Add a job with key {}".format(key_part))
            return
        top_char = top_char_list[depth]
        for tc in TOP_CHAR_IN_ENGLISH:
            offset = ord(top_char) - ord(tc)
            if offset < 0:
                offset += tools.common.TOTAL_CHAR_IN_ALPHABET
            cur_key_char = chr(ord('a') + offset)
            build_key(depth+1, key_part+cur_key_char)
    build_key(0, "")

def crack_file(filename):
    logging.info("[CRACK][MAIN] Try to crack file {}".format(filename))
    with open(filename) as f:
        global g_cipher_text
        g_cipher_text = f.read()
    prepare_crack_with_caesar()
    prepare_crack_with_vigenere(2)
    for i in range(0, 4):
        thread = CrackThread(i)
        thread.start()
    while(threading.activeCount() > 1):
        time.sleep(1)
    if (len(g_plain_text) > 0):
        logging.info("[CRACK][MAIN] Success!")
        with open("output.txt", 'w') as f:
            f.write(g_plain_text)
    else :
        logging.info("[CRACK][MAIN] Failed!")


def main():
    logging.info("[main] Engine Start!")
    global spell_checker
    spell_checker = spell_check.SpellChecker("dictionary.txt")
    global g_working_queue
    g_working_queue = queue.Queue()
    crack_file("encrypt_caesar.txt")
    logging.info("[main] Exit!")

if __name__ == "__main__":
    main()
