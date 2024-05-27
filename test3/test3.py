from judgetool import Pass, Fail, judge

from tabulate import tabulate

import argparse
import itertools
import math
import os
import pandas as pd
import re
import subprocess
import time


TOPOLOGIES = ["cycle", "tree", "sparse1", "sparse2", "dense"]
BAD_NEWS = "All tests failed..."

# https://discuss.python.org/t/add-built-in-flatmap-function-to-functools/21137/7
flatten = itertools.chain.from_iterable


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="test3.py", description="Tests your Programming Task 3 (PT 3) solution."
    )
    parser.add_argument(
        "-s",
        "--seed",
        default=int(0xC0DEBABE),
        help="random seed for test program (integer; default: decimal equivalent of 0xC0DEBABE)",
        type=int,
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-n",
        "--num-tests-each",
        default=5,
        help="number of tests to run per topology (integer; default: 5)",
        type=int,
    )
    group.add_argument(
        "-d",
        "--distribution",
        default=(5,) * 5,
        help="distribution of tests among topologies (5-element tuple; default: (1, 1, 1, 1, 1))",
        type=int,
        nargs=5,
        metavar=("CYCLE", "TREE", "SPARSE1", "SPARSE2", "DENSE"),
    )

    args = parser.parse_args()

    seed_arg = args.seed
    if args.num_tests_each != 5:
        distribution_arg = (args.num_tests_each,) * 5
    elif args.distribution != (5,) * 5:
        distribution_arg = args.distribution
    else:
        distribution_arg = (5,) * 5

    for i in range(5):
        if distribution_arg[i] < 0:
            print(
                f"ERROR\n\
\tYou're running a negative # of tests..."
            )
            exit()

    if not os.path.exists("task3.py"):
        print(
            f"ERROR\n\
\tAre you in the right folder?"
        )
        exit()

    outputs = {topology: [] for topology in TOPOLOGIES}
    errors = {topology: [] for topology in TOPOLOGIES}
    times = {topology: [] for topology in TOPOLOGIES}
    results = {topology: [] for topology in TOPOLOGIES}

    for index, topology in enumerate(TOPOLOGIES):
        for i in range(distribution_arg[index]):
            command = f"python3 -m cs145lib.task3.gen -s {i + seed_arg} -n {6 + i % 5} {topology} | \
                    python3 -m cs145lib.task3.test -v \
                    python3 task3.py > stdout.txt 2> stderr.txt"

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
            times[topology].append(time.time() - start_time)

            # Store output and error
            outputs[topology].append(output)
            errors[topology].append(error)

            results[topology].append(judge())

    data = {
        "Topology": TOPOLOGIES,
        "Tests": distribution_arg,
        "Frames": [0] * 5,
        "Bytes": [0] * 5,
        "Frames (average)": [0] * 5,
        "Bytes (average)": [0] * 5,
        "Successes": [0] * 5,
        "Failures": [0] * 5,
        "Timeouts": [0] * 5,
    }

    for i, topology in enumerate(TOPOLOGIES):
        for result, t in zip(results[topology], times[topology]):
            if t > 120:
                data["Timeouts"][i] += 1
            else:
                match result:
                    case Pass(f, b):
                        data["Successes"][i] += 1
                        data["Frames"][i] += f
                        data["Bytes"][i] += b
                    case Fail(logs):
                        data["Failures"][i] += 1
                        for log in logs:
                            print(log)
                        print()
        d = distribution_arg[i]
        data["Frames (average)"][i] = data["Frames"][i] / d if d > 0 else 0
        data["Bytes (average)"][i] = data["Bytes"][i] / d if d > 0 else 0

    df = pd.DataFrame(data)
    print()
    print(
        tabulate(
            df, headers="keys", showindex=False, tablefmt="outline", floatfmt=".3f"
        )
    )

    df_passed = df[df["Failures"] == 0]

    topologies_passed = df_passed.shape[0]
    test_cases_in_ave = df_passed["Tests"].sum()

    all_times = [*flatten([*times.values()])]
    ave_time = round(sum(all_times) / len(all_times), 3)

    if test_cases_in_ave == 0:
        ave_frames_used = 0
        ave_bytes_used = 0

        x = BAD_NEWS
    else:
        frames_used = df_passed["Frames"].sum()
        bytes_used = df_passed["Bytes"].sum()

        ave_frames_used = frames_used / test_cases_in_ave
        ave_bytes_used = bytes_used / test_cases_in_ave

        x = math.log2(5 * ave_frames_used + ave_bytes_used)

    multiplier = topologies_passed / 5
    failures = df["Failures"].sum()
    timeouts = df["Timeouts"].sum()

    print(
        f"""
    Starting seed\t\t{seed_arg}

    Average time\t\t{ave_time} s
    Average frames used\t\t{ave_frames_used}
    Average bytes used\t\t{ave_bytes_used}
    Failures\t\t\t{failures}
    Timeouts\t\t\t{timeouts}"""
    )

    if x == BAD_NEWS or x > 20:
        score = 0
    elif x >= 17:
        score = 50 - (35 / 3) * (x - 17)
    elif x >= 15.9:
        score = 70 - (20 / 1.1) * (x - 15.9)
    elif x >= 15.5:
        score = 80 - (10 / 0.4) * (x - 15.5)
    elif x >= 15.25:
        score = 90 - (10 / 0.25) * (x - 15.25)
    elif x >= 15.1:
        score = 98 - (8 / 0.15) * (x - 15.1)
    else:
        score = 100

    if timeouts >= 3:
        score = 0

    print(
        f"""
    X\t\t\t\t{x}
    Raw score\t\t\t{score}
    Multiplier\t\t\t{multiplier}
    Score\t\t\t{score * multiplier}{' (yay!)' if score == 100 else ''}
    """
    )
