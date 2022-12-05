import os
from timeit import default_timer as timer
from math import ceil

# A Huffman Tree Node
class Node:
    def __init__(self, prob, symbol, left=None, right=None):
        # probability of symbol
        self.prob = prob

        # symbol 
        self.symbol = symbol

        # left node
        self.left = left

        # right node
        self.right = right

        # tree direction (0/1)
        self.code = ''

""" A helper function to print the codes of symbols by traveling Huffman Tree"""
codes = dict()
size_before_compression = 0
size_after_compression = 0
res = []

def Calculate_Codes(node, val=''):
    # huffman code for current node
    newVal = val + str(node.code)

    if(node.left):
        Calculate_Codes(node.left, newVal)
    if(node.right):
        Calculate_Codes(node.right, newVal)

    if(not node.left and not node.right):
        codes[node.symbol] = newVal
         
    return codes        

""" A helper function to calculate the probabilities of symbols in given data"""
def Calculate_Probability(data):
    symbols = dict()
    for element in data:
        if symbols.get(element) == None:
            symbols[element] = 1
        else: 
            symbols[element] += 1     
    return symbols

""" A helper function to obtain the encoded output"""
def Output_Encoded(data, coding):
    encoding_output = []
    for c in data:
      #  print(coding[c], end = '')
        encoding_output.append(coding[c])
        
    string = ''.join([str(item) for item in encoding_output])    
    return string
        
""" A helper function to calculate the space difference between compressed and non compressed data"""    
def Total_Gain(data, coding):
    global size_before_compression, size_after_compression

    before_compression = len(data) * 8 # total bit space to stor the data before compression
    after_compression = 0
    symbols = coding.keys()
    for symbol in symbols:
        count = data.count(symbol)
        after_compression += count * len(coding[symbol]) #calculate how many bit is required for that symbol in total
    size_before_compression = before_compression
    size_after_compression = after_compression         
    print("Space usage before compression (in bits):", size_before_compression)    
    print("Space usage after compression (in bits):",  size_after_compression)
    print("Compression ratio  = ", before_compression / after_compression)


def Huffman_Encoding(data):
    symbol_with_probs = Calculate_Probability(data)
    symbols = symbol_with_probs.keys()
    probabilities = symbol_with_probs.values()
    print("symbols: ", symbols)
    print("probabilities: ", probabilities)
    
    nodes = []
    
    # converting symbols and probabilities into huffman tree nodes
    for symbol in symbols:
        nodes.append(Node(symbol_with_probs.get(symbol), symbol))
    
    while len(nodes) > 1:
        # sort all the nodes in ascending order based on their probability
        nodes = sorted(nodes, key=lambda x: x.prob)
        # for node in nodes:  
        #      print(node.symbol, node.prob)
    
        # pick 2 smallest nodes
        right = nodes[0]
        left = nodes[1]
    
        left.code = 0
        right.code = 1
    
        # combine the 2 smallest nodes to create new node
        newNode = Node(left.prob+right.prob, left.symbol+right.symbol, left, right)
    
        nodes.remove(left)
        nodes.remove(right)
        nodes.append(newNode)
            
    huffman_encoding = Calculate_Codes(nodes[0])
    print("symbols with codes", huffman_encoding)
    Total_Gain(data, huffman_encoding)
    encoded_output = Output_Encoded(data,huffman_encoding)
    return encoded_output, nodes[0]  
    
 
def Huffman_Decoding(encoded_data, huffman_tree):
    tree_head = huffman_tree
    decoded_output = []
    for x in encoded_data:
        if x == '1':
            huffman_tree = huffman_tree.right   
        elif x == '0':
            huffman_tree = huffman_tree.left
        try:
            if huffman_tree.left.symbol == None and huffman_tree.right.symbol == None:
                pass
        except AttributeError:
            decoded_output.append(huffman_tree.symbol)
            huffman_tree = tree_head
        
    string = ''.join([str(item) for item in decoded_output])
    return string        


def doHuffman(file_name):
    
    datasize = os.path.getsize(file_name)
    with open(file_name, "r") as f:
        data_content = f.read()

    start = timer()
    encoding, tree = Huffman_Encoding(data_content)
    end = timer()
    encode_time = end - start

    enc_msg_file = "./Encoded_Files/" + file_name.split('/')[-1].split('.')[0] + "_Huffman_encoded"
    with open(enc_msg_file, "w+") as f:
        f.write(encoding)
    # print("Encoded output", encoding)

    start = timer()
    decode_output = Huffman_Decoding(encoding,tree)
    end = timer()
    decode_time = end - start

    if data_content == decode_output:
        print("Original and Decoded file MATCH")
    else:
        print("Original and Decoded file DO NOT MATCh")

    decode_to_file = "./Decoded_Files/" + file_name.split('/')[-1].split('.')[0] + "_Huffman_decoded"
    with open(decode_to_file, "w+") as f:
        f.write(encoding)

    print("data size = ", datasize)
    print("Encoding Time = ", encode_time)
    print("Deconding Time = ", decode_time)
    print()

    return (size_before_compression//8)/1024, ceil(size_after_compression/8)/1024, encode_time, decode_time