from judgetool import Pass, Fail, judge

import argparse
import math
import os
import subprocess
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="test2.py", description="Tests your Programming Task 2 (PT 2) solution."
    )

    parser.add_argument(
        "-s",
        "--seed",
        default=int(0xC0DEBABE),
        help="Random seed for test program (integer; default: decimal equivalent of 0xC0DEBABE).",
        type=int,
    )
    parser.add_argument(
        "-n",
        "--num-tests",
        default=50,
        help="Number of tests to run (integer; default: 50).",
        type=int,
    )

    args = parser.parse_args()

    seed_arg, num_tests_arg = args.seed, args.num_tests

    if not os.path.exists("task2.py"):
        print(
            f"ERROR\n\
            \tAre you in the right folder?"
        )
        exit()

    print(f"Running {num_tests_arg} tests...")
    if num_tests_arg > 5:
        print("This may take a while...")

    outputs = []
    errors = []
    times = []
    results = []
    # Loop through seeds from 0 to num_tests_arg
    for i in range(num_tests_arg):
        # Construct the command with the current seed
        command = f"python3 -m cs145lib.task2.gen --seed {i + seed_arg} | \
                python3 -m cs145lib.task2.test --quiet \
                python3 task2.py"

        # Time the process
        start_time = time.time()

        # Run the command and capture the output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Read the output and errors
        output, error = process.communicate()

        # Calculate elapsed time
        times.append(time.time() - start_time)

        # Store output and error
        outputs.append(output)
        errors.append(error)

        results.append(judge())

    frames_used = 0
    bytes_used = 0
    failures = 0
    timeouts = 0

    for result, t in zip(results, times):
        if t > 20:
            timeouts += 1
        else:
            match result:
                case Pass(f, b):
                    frames_used += f
                    bytes_used += b
                case Fail(_):
                    failures += 1

    ave_time = round(sum(times) / len(times), 3)
    ave_frames_used = frames_used / num_tests_arg
    ave_bytes_used = bytes_used / num_tests_arg
    x = math.log2(5 * ave_frames_used + ave_bytes_used)

    print(
        f"""
    Tests ran\t\t\t{num_tests_arg}
    Starting seed\t\t{seed_arg}

    Average time\t\t{ave_time} s
    Average frames used\t\t{ave_frames_used}
    Average bytes used\t\t{ave_bytes_used}
    X\t\t\t\t{x}
    Failures\t\t\t{failures}
    Timeouts\t\t\t{timeouts}"""
    )

    if x > 16.6:
        score = 0
    elif x >= 15.5:
        score = 60 - (10 / 1.1) * (x - 15.5)
    elif x >= 14.6:
        score = 70 - (10 / 0.9) * (x - 14.6)
    elif x >= 14:
        score = 80 - (10 / 0.6) * (x - 14)
    elif x >= 13.55:
        score = 90 - (10 / 0.45) * (x - 13.55)
    elif x >= 13.41:
        score = 98 - (8 / 0.14) * (x - 13.41)
    else:
        score = 100

    score -= 25 * failures
    score = max(0, score)

    if timeouts >= 3:
        score = 0

    print(
        f"""
    Score\t\t\t{score}{' (yay!)' if score == 100 else ''}
    """
    )
