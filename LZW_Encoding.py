import sys
from sys import argv
from struct import *
from timeit import default_timer as timer
from os.path import getsize
from difflib import SequenceMatcher

def encode_file(file_to_encode):
    '''
        Encodes the file using LZW encoding

        Parameters:
            file_to_encoded: name of the file to be encoded

        Return:
            name of the encoded file
    '''
    maximum_table_size = pow(2,int(16))      
    file = open(file_to_encode)                 
    data = file.read()                      
    file.close()

    # Initialize the character map to the ASCII value for each key from 0 - 255
    size = 256                   
    char_map = {chr(i): i for i in range(size)}    
    string = ""             
    encoded_msg = []    

    # Iterate through each symbol in the input data and encode it based on the char map
    # Adds to the map when a combination of symbols is found
    for symbol in data:                     
        string_plus_symbol = string + symbol
        if string_plus_symbol in char_map: 
            string = string_plus_symbol
        else:
            encoded_msg.append(char_map[string])
            if(len(char_map) <= maximum_table_size):
                char_map[string_plus_symbol] = size
                size += 1
            string = symbol

    # Add the last string to the encoded message if required
    if string in char_map:
        encoded_msg.append(char_map[string])

    # Write the encoded data into a file
    enc_file = "./Encoded_Files/" + file_to_encode.split('/')[-1].split('.')[0] + "_LZW_encoded"
    
    print()
    print("LZW: Symbol Table")
    print(char_map)

    with open(enc_file, "wb") as output_file:
        for data in encoded_msg:
            output_file.write(pack('>H',int(data)))
            
    return enc_file

def decode_file(encoded_file, decode_to_file):
    '''
        Decodes the file using LZW encoding

        Parameters:
            encoded_file: name of the file to be encoded
            decode_to_file: name of the file used while writing the decoded output

        Return:
            None
    '''
    encoded_msg = []
    next_code = 256
    deencoded_msg = ""
    string = ""

    # Read the encoded file
    with open(encoded_file, "rb") as file:
        while True:
            rec = file.read(2)
            if len(rec) != 2:
                break
            (data, ) = unpack('>H', rec)
            encoded_msg.append(data)

    # Initialize the character map to the ASCII value for each key from 0 - 255 as done in encoding
    size = 256
    char_map = dict([(x, chr(x)) for x in range(size)])

    # Iterate through each encoded value and dencode it based on the char map
    # Adds to the map when a combination of symbols is found
    for code in encoded_msg:
        if not (code in char_map):
            char_map[code] = string + (string[0])
        deencoded_msg += char_map[code]
        if not(len(string) == 0):
            char_map[next_code] = string + (char_map[code][0])
            next_code += 1
        string = char_map[code]

    # Write the decoded output to the file
    with open(decode_to_file, "w") as output_file:
        for data in deencoded_msg:
            output_file.write(data)

def get_compression_ratio(original_file, encoded_file):
    """
    Helper function to calculate compression ratio

    Parameters:
        original_file: Name of the original file
        encoded_file: Name of the encoded file
    Return:
        Original file size, Encoded file size, Compression ratio
    """
    og_size = getsize(original_file)
    enc_size = getsize(encoded_file)

    ratio = og_size/enc_size
    return og_size, enc_size, ratio

def verify(original_file, decoded_file):   
    """
    Verifies if the original and decoded file match

    Parameters:
        original_file: Name of the original file
        decoded_file: Name of the decoded file
    Return:
        True if the files match, false otherwise
    """ 
    text1 = open(original_file).read()
    text2 = open(decoded_file).read()
    m = SequenceMatcher(None, text1, text2)
    
    if m.ratio() == 1.0:
        return True
    
    return False

def do_Lempel_Ziv_Welch(file_to_be_encoded):
    """
    Driver function for LZW

    Parameters:
        file_to_be_encoded: name of the file to be encoded
    
    Return:
        Original file size in kB, Encoded file size in kB, Time taken for encoding, Time taken for decoding
    """
    start = timer()
    encoded_file = encode_file(file_to_be_encoded)
    end = timer()

    enc_time = end - start

    decode_to_file = "./Decoded_Files/" + file_to_be_encoded.split('/')[-1].split('.')[0] + "_LZW_decoded"

    start = timer()
    decode_file(encoded_file, decode_to_file)
    end = timer()

    dec_time = end - start

    print(enc_time, dec_time)

    og_size, enc_size, ratio = get_compression_ratio(file_to_be_encoded, encoded_file)

    result = verify(file_to_be_encoded, decode_to_file)
    print("Original and Decoded file", "MATCH!" if result == 1.0 else "DO NOT MATCH!")
    
    return (og_size/1024, enc_size/1024, enc_time, dec_time)




