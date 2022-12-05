
from decimal import Decimal, getcontext
from difflib import SequenceMatcher
from os.path import getsize
from timeit import default_timer as timer

getcontext().prec=128

class ArithmeticEncoding:
    def __init__(self, frequency_table):
        self.probability_table = self.get_probability_table(frequency_table)

    def get_probability_table(self, frequency_table):
        total_frequency = sum(list(frequency_table.values()))

        probability_table = {}
        for key, value in frequency_table.items():
            probability_table[key] = value/total_frequency

        return probability_table

    def get_encoded_value(self, encoder):
        last_stage = list(encoder[-1].values())
        last_stage_values = []
        for sublist in last_stage:
            for element in sublist:
                last_stage_values.append(element)

        last_stage_min = min(last_stage_values)
        last_stage_max = max(last_stage_values)

        return (last_stage_min + last_stage_max)/2

    def process_stage(self, probability_table, stage_min, stage_max):
        stage_probs = {}
        stage_domain = stage_max - stage_min
        for term_idx in range(len(probability_table.items())):
            term = list(probability_table.keys())[term_idx]
            term_prob = Decimal(probability_table[term])
            cum_prob = term_prob * stage_domain + stage_min
            stage_probs[term] = [stage_min, cum_prob]
            stage_min = cum_prob
        return stage_probs

    def encode(self, msg, probability_table):

        encoder = []

        stage_min = Decimal(0.0)
        stage_max = Decimal(1.0)
        
        for msg_term_idx in range(len(msg)):
            stage_probs = self.process_stage(probability_table, stage_min, stage_max)

            msg_term = msg[msg_term_idx]
            stage_min = stage_probs[msg_term][0]
            stage_max = stage_probs[msg_term][1]

            encoder.append(stage_probs)

        stage_probs = self.process_stage(probability_table, stage_min, stage_max)
        encoder.append(stage_probs)

        encoded_msg = self.get_encoded_value(encoder)

        return encoder, encoded_msg

    def decode(self, encoded_msg, msg_length, probability_table):

        decoder = []
        decoded_msg = ""

        stage_min = Decimal(0.0)
        stage_max = Decimal(1.0)

        for _ in range(msg_length):
            stage_probs = self.process_stage(probability_table, stage_min, stage_max)

            for msg_term, value in stage_probs.items():
                if encoded_msg >= value[0] and encoded_msg <= value[1]:
                    break

            decoded_msg = decoded_msg + msg_term
            stage_min = stage_probs[msg_term][0]
            stage_max = stage_probs[msg_term][1]

            decoder.append(stage_probs)

        stage_probs = self.process_stage(probability_table, stage_min, stage_max)
        decoder.append(stage_probs)

        return decoder, decoded_msg


def encode_file(file_to_be_encoded):
  freq_table = {}
  with open(file_to_be_encoded) as f:
      for line in f.readlines():
          for char in line:
              if char not in freq_table:
                  freq_table[char] = 1
              else:
                  freq_table[char] += 1

  AE = ArithmeticEncoding(freq_table)

  print()
  print("Arithmetic Encoding Probability table")
  print(AE.probability_table)
  encoded_msg_len = []

  enc_msg_file = "./Encoded_Files/" + file_to_be_encoded.split('/')[-1].split('.')[0] + "_AE_encoded"
  with open(enc_msg_file, "w") as enc_file:
    with open(file_to_be_encoded) as f:
        for line in f.readlines():
            encoded_msg_len.append(len(line))
            _, encoded_msg = AE.encode(msg=line,
                                    probability_table=AE.probability_table)
            enc_file.write(str(encoded_msg))
            enc_file.write("\n")

  return enc_msg_file, encoded_msg_len, freq_table

def decode_file(encoded_file, encoded_msg_len, frequency_table, decode_to_file):
    dec_file = open(decode_to_file, "w")
    AE = ArithmeticEncoding(frequency_table)

    with open(encoded_file) as enc_file:
        for i, encoded_msg in enumerate(enc_file.readlines()):
            _, decoded_msg = AE.decode(encoded_msg=Decimal(encoded_msg),
                                  msg_length=encoded_msg_len[i],
                                  probability_table=AE.probability_table)
            dec_file.write(decoded_msg)    

    dec_file.close()

def verify(original_file, decoded_file):    
    text1 = open(original_file).read()
    text2 = open(decoded_file).read()
    m = SequenceMatcher(None, text1, text2)
    
    if m.ratio() == 1.0:
        return True
    
    return False

def get_compression_ratio(original_file, encoded_file):
    og_size = getsize(original_file)
    enc_size = 0
    with open(encoded_file) as f:
        enc_size = 16 * len(f.readlines())

    ratio = og_size/enc_size
    return og_size, enc_size, ratio

def do_Arithmetic_Encoding(file_to_be_encoded):

    start = timer()
    encoded_file, encoded_msg_len, freq_table = encode_file(file_to_be_encoded)
    end = timer()

    enc_time = end - start

    decode_to_file = "./Decoded_Files/" + file_to_be_encoded.split('/')[-1].split('.')[0] + "_AE_decoded"

    start = timer()
    decode_file(encoded_file, encoded_msg_len, freq_table, decode_to_file)
    end = timer()

    dec_time = end - start

    og_size, enc_size, ratio = get_compression_ratio(file_to_be_encoded, encoded_file)

    result = verify(file_to_be_encoded, decode_to_file)
    print("Original and Decoded file", "MATCH!" if result == 1.0 else "DO NOT MATCH!")
    
    return (og_size/1024, enc_size/1024, enc_time, dec_time)
