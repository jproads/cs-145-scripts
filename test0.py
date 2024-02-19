# Must be placed in same folder as task0.py and cs145lib

import subprocess
from math import log2 
import time  

SEED = int(0xC0DEBABE)

if __name__ == '__main__':
    outputs = []
    errors = []
    times = []
    # Loop through seeds from 0 to 99
    for i in range(100):
        # Construct the command with the current seed
        command = f"python3 -m cs145lib.task0.make_sentence --seed {i + SEED} | \
                python3 -m cs145lib.task0.test --seed {i + SEED} \
                python3 task0.py"
        
        # Time the process
        start_time = time.time()
    
        # Run the command and capture the output
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read the output and errors
        output, error = process.communicate()

        # Calculate elapsed time
        times.append(time.time() - start_time)
        
        # Store output and error
        outputs.append(output)
        errors.append(error)

    # Parse each output
    total_bits = 0
    test_errors = 0
    time_errors = 0
    for i, (output, error, t) in enumerate(zip(outputs, errors, times)):
        output_list = output.split()
        bits = int(output_list[1])
        received_msg = output_list[15:]

        # Parse error
        sent_msg = error.split()[8:]

        received_str = " ".join(received_msg)
        sent_str = " ".join(sent_msg)
        if received_msg != sent_msg or t >= 10:
            print(f'ERROR FOR SEED {i + SEED}:\n\
                \tBits: {bits}\n\
                \tTime: {t} s\n\
                \tSent: {sent_str}\n\
                \tReceived: {received_str}')
            test_errors += 1
        else:
            total_bits += bits
        
        if t >= 10:
            time_errors += 1
    
    # Display results
    print(f'TESTS\n\
            \tSeed: {SEED}\n\
            \tTests performed: {len(outputs)}\n\
            \tTests timed out: {time_errors}\n\
            \tFailed tests: {test_errors}')
    
    # End if all tests failed - otherwise we encounter div-by-0 errors
    if test_errors == len(outputs):
        exit()

    # Compute score
    avg = total_bits / (len(outputs) - test_errors)
    x = log2(total_bits)
    if time_errors >= 3:
        score = 0
    elif x > 18.8:
        score = 0
    elif x < 12.8:
        score = 100
    else:
        score = 154 - 5 * x

    score -= test_errors * 1.5

    if score < 0:
        score = 0

    print(f'PERFORMANCE\n\
            \tTotal bits: {total_bits}\n\
            \tAverage bits per message: {avg}\n\
            \tX: {x}\n\
            \tScore: {score}')