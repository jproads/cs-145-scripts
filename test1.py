# Must be placed in same folder as task1.py and cs145lib

import argparse
import subprocess
from math import log2 
import os
import time  

DEFAULT_NUM_TESTS = 100

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="test0.py", description="Tests your Programming Task 1 (PT 1) solution.")

    parser.add_argument("-s", "--seed", default=int(0xC0DEBABE), help="Random seed for test program (integer; default: decimal equivalent of 0xC0DEBABE).", type=int)
    parser.add_argument("-n", "--num-tests", default=100, help="Number of tests to run (integer; default: 100).", type=int)

    args = parser.parse_args()

    seed_arg, num_tests_arg = args.seed, args.num_tests

    if not os.path.exists("task1.py"):
        print(f'ERROR\n\
            \tAre you in the right folder?')
        exit()

    outputs = []
    errors = []
    times = []
    # Loop through seeds from 0 to num_tests_arg
    for i in range(num_tests_arg):
        # Construct the command with the current seed
        command = f"python3 -m cs145lib.task1.make_sentence --seed {i + seed_arg} | \
                python3 -m cs145lib.task1.test --seed {i + seed_arg} \
                python3 task1.py"
        
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
            print(f'ERROR FOR SEED {i + seed_arg}:\n\
                \tBits: {bits}\n\
                \tTime: {t} s\n\
                \tSent: {sent_str}\n\
                \tReceived: {received_str}')
            test_errors += 1
            
        total_bits += bits
        
        if t >= 10:
            time_errors += 1
    
    # Display results
    print(f'TESTS\n\
            \tSeed: {seed_arg}\n\
            \tTests performed: {len(outputs)}\n\
            \tTests timed out: {time_errors}\n\
            \tFailed tests: {test_errors}')
    
    # End if all tests failed - otherwise we encounter div-by-0 errors
    if test_errors == len(outputs):
        exit()

    # Compute score
    avg = total_bits / len(outputs)
    x = log2(total_bits if num_tests_arg == DEFAULT_NUM_TESTS else avg * DEFAULT_NUM_TESTS)
    if time_errors >= 3:
        score = 0
    elif x > 21.99:
        score = 0
    elif x < 16.99:
        score = 100
    else:
        score = 214 - 7 * x

    # 1% of test cases failed = -1.5
    score -= (test_errors / (num_tests_arg * 0.01)) * 1.5

    if score < 0:
        score = 0

    print(f'PERFORMANCE\n\
            \tTotal bits: {total_bits}\n\
            \tAverage bits per message: {avg}\n\
            \tX: {x}\n\
            \tScore: {score}')

    if num_tests_arg != 100:
        print(f'NOTE\n\
            \tNumber of tests is not 100.\n\
            \tScore here might not accurately reflect correctness of solution:\n\
            \t- Average bits per message was used to determine X.\n\
            \t- Penalties were scaled according to number of tests ran.')
