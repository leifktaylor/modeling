# ciphers.py
# Author: Leif Taylor, September 2016
# ciphers.py encrypts files with a 'witch's brew' of ciphers.
# upon encryption of a file, a key is created.
# good luck decrypting the 'cipher-mixtape' without the key.

# v.1.0
# note: currently whitespace and indentation isn't perfectly preserved.  Be careful
# when encrypting files where this matters.
# note: currently doesn't support input files that use unicode, only ascii is supported.
#TODO: Solve issue with preserving whitespace
#TODO: Add Unicode support.

import enchant
import random
import re
import wordlist
import string
import json
import argparse

default_word_list = ''

def init_dictionary():

    enchant_dict = enchant.Dict('en_US')
    return enchant_dict

def generate_substitution_cipher():
    """
    Replacement: Creates a simple substitution cipher from a list of ASCII characters.

    :return: cipher_dict, and a key_dict
    """
    ch_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    cipher_list = list(ch_list)
    random.shuffle(cipher_list)
    cipher_dict = dict(zip(ch_list, cipher_list))
    key_dict = dict(zip(cipher_list, ch_list))
    return cipher_dict, key_dict

def shuffle_encrypt(string, multiplier=10):
    """
    Scrambles characters in a string and returns the encrypted string, and the key to unscramble.
    Unscramble with shuffle_decrypt_string
    :param string: The string to encrypt
    :param multiplier: (default 10) How many shuffle iterations.
    :return: encrypted string, unscramble key
    :return: unscramble key
    """
    #TODO: Solve issue with preserving whitespace.
    unscramble_key = []
    scramble_key = []
    ch_list = string.split()
    # ch_list = re.split(r'(\s+)', string) # <-- preserves white space maybe ...
    ch_len = len(ch_list) - 1
    # Create a list of shuffling actions. The movement of each individual unit being shuffled
    # Is stored in the list 'unscramble_key'.
    # This loop will generate an unscramble key, and the 'key' of actions used to scramble in the first place.
    for i in range(0, ch_len*multiplier):
        character_to_shift = random.randint(0, ch_len)
        place_to_shift_to = random.randint(0, ch_len)
        this_shift = (place_to_shift_to, character_to_shift)
        un_shift = (character_to_shift, place_to_shift_to)
        unscramble_key.insert(0, un_shift)
        scramble_key.append(this_shift)

    # Shuffle the original string using the scramble_key
    for i in range(0, len(scramble_key)):
        character_to_shift = scramble_key[i][1]
        place_to_shift_to = scramble_key[i][0]
        ch_list.insert(place_to_shift_to, ch_list.pop(character_to_shift))
    encrypted_string = ' '.join(ch_list)
    return encrypted_string, unscramble_key

def shuffle_decrypt(string, unscramble_key):
    """
    Decrypts a shuffle-encrypted string using an unscramble_key

    :param string: shuffle-encrypted string
    :param unscramble_key: unscramble key
    :return:
    """
    ch_list = string.split()
    # ch_list = re.split(r'(\s+)', string) # <--- preserves white space maybe
    # Unshuffle the string using the unscramble_key
    for i in range(0, len(unscramble_key)):
        character_to_shift = unscramble_key[i][1]
        place_to_shift_to = unscramble_key[i][0]
        ch_list.insert(place_to_shift_to, ch_list.pop(character_to_shift))
    unscrambled_string = ' '.join(ch_list)
    return unscrambled_string


def substitute_encrypt(input_string, cipher_dict=''):
    """
    Encrypts string using a replacement dict created by generate_cipher(type='replacement')

    :param input_string: string to encrypt
    :param cipher_dict: (optional) generated cipher dictionary
    :return: encrypted string, and a cipher key dict
    """
    if not cipher_dict:
        cipher_dict, key_dict = generate_substitution_cipher()
    encrypted_string = ''.join(cipher_dict.get(ch, ch) for ch in input_string)
    return encrypted_string, key_dict

def substitute_decrypt(input_string, cipher_key):
    """
    Decrypts substitution cipher using a cipher key dictionary.

    :param input_string: Encrypted string to decrypt.
    :param cipher_key: Cipher key dictionary
    :return: Decrypted string
    """
    decrypted_string = ''.join(cipher_key.get(ch, ch) for ch in input_string)
    return decrypted_string

def brute_force_substitution_cipher(input_string, wordlist_file=default_word_list, accuracy_percent=.01, attempts=1000000):
    """
    Attempts to find the cipher dictionary for the given encrypted string, by randomly
    generating a cipher_dict and decrypting the input_string.  If when applied to the string,
    the decrypt results in enough words that match words in the wordlist, the test will
    assume that the document is properly decrypted and stop running.  The larger the wordlist,
    the higher the chance of true success, but the slower the brute-force alg will run.

    :param input_string: encrypted string
    :param wordlist_file: path to wordlist file
    :param accuracy_percent: the amount of matches (percent) that must be found in the word list. e.g. .50
    :param attempts: number of times to generate a new cipher and test it against the input string
    :return: decrypted string, and cipher key dictionary
    """

    #BETTER WAY TO DO THIS:
    # Decrypt a single word in the string with random ciphers
    # If that word is matched in the wordlist, check the entire string
    # If the first word is never matched, move onto the second word and repeat
    # Continue until you have reached match requirement or end of string.
    # WAY BETTER WAY:
    # TODO: Use actual cipher decoding techniques which use:
    # Letter frequency (search for most frequent letter and assume e, or t.
    # Use small words (single letter words usually 'a' or 'I')

    # fix improper accuracy percent input
    if accuracy_percent > 1:
        if accuracy_percent <= 100:
            accuracy_percent = accuracy_percent/100
        else:
            print('Improper accuracy percent given, setting to default')
            logging.debug('Improper accuracy percent given. Setting to default')

    # open word_list file put into list
    #word_list = open_file_to_list(wordlist_file)
    #word_list = word_list.split()
    word_list = ['hello', 'how', 'are', 'you', 'my', 'name', 'is', 'leif']

    # count words in word_list
    word_list_count = len(word_list)

    for i in range(0, attempts):
        # generate a random cipher_key
        crypt_cipher, crypt_key = generate_substitution_cipher()
        dc_string = substitute_decrypt(input_string, crypt_key)
        # split string into list
        string_list = dc_string.split()
        # count words in string_list
        string_list_count = len(string_list)
        match_counter = 0

        # check if string_list[i] in word_list (case insens.) <--if current_word in (name.upper() for name in word_list)
        # if it is:
        for i in range(0, string_list_count): # - 1 here??
            for current_word in range(0, word_list_count): # - 1 here??
                if current_word in (word.upper() for word in word_list):
                    print('MATCH! {0} matches word in wordlist!'.format(current_word))
                    match_counter += 1
            print('Found {0} matches.'.format(match_counter))

        # confirm match counter meets accuracy requirements
        print('match_counter: ', match_counter)
        if (match_counter / string_list_count) >= accuracy_percent:
            print(dc_string)
            logging.info('Accurate cipher match found, decrypted string and cipher key')
            print('Cipher Match Found!')
            logging.info(dc_string)
            break
    return dc_string, crypt_key

def full_encrypt(input_string):
    """
    Encrypts a string with a substitution cipher and a shuffle cipher.

    :param input_string: String to be encrypted
    :return: encrypted string, and a dictionary with cipher key
    """
    sub_cipher_string, sub_k = substitute_encrypt(input_string)
    full_cipher_string, shuffle_k = shuffle_encrypt(sub_cipher_string)
    full_key = {'shuffle_key': shuffle_k, 'substitution_key': sub_k}
    return full_cipher_string, full_key

def full_decrypt(cipher_string, full_key):
    """
    Decrypts a string encrypted with 'full_encrypt'.

    :param cipher_string: Encrypted string to be decrypted
    :param full_key: Key given from 'full_encrypt'
    :return:
    """
    un_shuffle_string = shuffle_decrypt(cipher_string, full_key['shuffle_key'])
    un_sub_string = substitute_decrypt(un_shuffle_string, full_key['substitution_key'])
    return un_sub_string

def encrypt_file(filename, outputname):
    """
    Fully encrypts a file by copying and saving to an output file.
    Also saves a key with 'filename.key'

    :param filename: The file to encrypt
    :param outputname: The name of the output file to save to
    :return:
    """
    try:
        decrypt_key = []
        text_list = open_file_to_list(filename)
        # Encrypt File
        for line in text_list:
            r, k = full_encrypt(line)
            decrypt_key.append(k)
            file_object = write_to_file(r+'\n', outputname, 'a', False)
        file_object.close()
        # Create Key File
        key_file = str(outputname.split('.', 1)[0]) + '.key'
        with open(key_file, 'w') as output_key_file:
            json.dump(decrypt_key, output_key_file)
        output_key_file.close()
        print('{0} encrypted. Saved as {1}'.format(filename, outputname))
    except IOError:
        print('Could not find {0}. Does it exist?'.format(filename))


def decrypt_file(input_file, outputname, keyfile=''):
    """
    Decrypts file that has been encrypted with 'encrypt_file'
    Defaults to using keyfile with same name as input_file


    :param input_file: filename/path of file to decrypt
    :param outputname: new file to output to
    :param keyfile: name of keyfile, of none supplied searches for 'input_file.key'
    :return:
    """
    try:
        # Open keyfile
        if not keyfile:
            key_filename = str(input_file.split('.', 1)[0]) + '.key'
        with open(key_filename, 'r') as key_file_object:
            decrypt_key_list = json.load(key_file_object)
        text_list = open_file_to_list(input_file)
        decrypted_lines = []
        # Decrypt lines from file using key
        for line in range(0, len(text_list)):
            decrypted_lines.append(full_decrypt(text_list[line], decrypt_key_list[line]))
        # Write decrypted lines to new file
        for line in decrypted_lines:
            open_file = write_to_file(str(line)+'\n', outputname, 'a', False)
        open_file.close()
        print('{0} decrypted. Saved as {1}'.format(input_file, outputname))
    except IOError:
        print('Input file or keyfile not found. Check file names')


def open_file_to_list(filename):
    """
    Opens a file and reads each line into a list of lines.

    :param filename: path to file
    :return: List of lines
    """
    try:
        with open(filename) as f:
            line_list = f.readlines()
        f.close()
        return line_list
    except IOError:
        print('Could not find {0}. Does it exist?'.format(filename))
        raise



def write_to_file(input_string, filename, style='w', close=True):
    """
    Writes input string to file

    :param input_string: string to write to output file
    :param filename: name of file to output to
    :param style: 'a' for append, or 'w' for write (default)
    :return: output_file object
    """
    try:
        with open(filename, style) as output_file:
            output_file.write(input_string)
        if close:
            output_file.close()
        return output_file
    except IOError:
        print('Could not find {0}. Does it exist?'.format(filename))
        raise

def parseArguments():
    """
    Parses arguments given at commandline.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="File you wish to encrypt.")
    parser.add_argument("output_file", help="Output file name of encrypted file")
    parser.add_argument("enc_type", help="'e' or 'd' for encrypt or decrypt")
    parser.add_argument("-k", "--dec_k", help="Decryption key filename", default='')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Get arguments
    args = parseArguments()
    enc_type = args.enc_type
    inp_file = args.input_file
    out_file = args.output_file
    dec_k = args.dec_k

    # Run Program
    if enc_type not in ['e', 'd']:
        print("Please use 'e' for Encrypt or 'd' for Decrypt.  Use -h for help.")
    else:
        if enc_type == 'e':
            # Encrypt file
            encrypt_file(inp_file, out_file)
        if enc_type == 'd':
            # Decrypt file
            if not dec_k:
                decrypt_file(inp_file, out_file)
            else:
                decrypt_file(inp_file, out_file, dec_k)

