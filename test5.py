import argparse
import json
import math
import os
import signal
import subprocess

from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class Pass:
    messages_used: int
    bytes_used: int
    time_taken: float


@dataclass
class Fail:
    logs: list[str]


def clamp(x: float, l: float, h: float) -> float:
    if x < l:
        return l
    elif x > h:
        return h
    else:
        return x


def approx(a: float, b: float, tol: float = 10**-6) -> bool:
    return abs(a - b) < tol


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise Exception("timeout")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="test5.py", description="Tests your Programming Task 5 (PT 5) solution."
    )
    parser.add_argument(
        "-f",
        "--file",
        default="task5.py",
        help="name of program to test (string; default: task5.py)",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--seed",
        default=int(0xC0DEBABE),
        help="random seed for test program (integer; default: decimal equivalent of 0xC0DEBABE)",
        type=int,
    )
    parser.add_argument(
        "-tl",
        "--time-limit",
        default=60,
        help="time limit (in seconds) to give your program (integer; default: 60)",
        type=int,
    )

    args = parser.parse_args()

    if not os.path.isdir("tests"):
        os.mkdir("tests")

    reused_tests: int = 0

    print()
    print("\tGenerating tests...")
    for i in range(30):
        filename = f"tests/{args.seed + i}.txt"
        if not os.path.isfile(filename):
            command = f"python3 -m cs145lib.task5.gen -s {args.seed + i} > {filename}"
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output, error = process.communicate()
        else:
            reused_tests += 1
    print(f"\tDone generating tests! (reused {reused_tests} tests)")
    print()

    results: list[Pass | Fail] = []
    total_elapsed: float = 0

    for i in range(30):
        filename = f"tests/{args.seed + i}.txt"
        command = f"cat {filename} | \
                    python3 -m cs145lib.task5.test  python3 {args.file}"

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            with time_limit(45):
                output, error = process.communicate()
        except:
            results.append(Fail(["-- time limit exceeded"]))
            break

        try:
            with open("output.json", "r") as f:
                data = json.loads(f.read())

                m = sum(data["total_send_cts_from"].values())
                b = sum(data["total_send_lns_from"].values())
                t = data["elapsed"]
                passed = data["correct"]

                if total_elapsed + t > args.time_limit:
                    break

                if passed:
                    results.append(Pass(m, b, t))
                    total_elapsed += t
                else:
                    results.append(Fail(["-- wrong answer given"]))
                    break
        except Exception as e:
            results.append(Fail([repr(e)]))

    if len(results) > 0:
        print("\tTest #\t\tSeed\t\tResult\t\tMessages\tBytes\t\tTime")
        print()

    failed: bool = False
    mt: int = 0
    bt: int = 0

    for i, result in enumerate(results, start=1):
        match result:
            case Pass(m, b, t):
                print(
                    f"\t{i}\t\t{str(args.seed+i-1).ljust(10)}\tPass\t\t{m}\t\t{b}\t\t{t}"
                )
                mt += m
                bt += b
            case Fail(l):
                print(f"\t{i}\t\t{str(args.seed+i-1).ljust(10)}\tFail\t\t-\t\t-\t\t-")
                print()
                for log in l:
                    print(f"\t\t{log}")
                print()
                failed = True
    print()

    t = len(results)
    tp = clamp((t - 2) / 28, 0, 1)

    if mt > 0 and bt > 0:
        x = math.log2(5 * (mt / t) + (bt / t))
        xp = clamp((12.5 - x) / 3.4, 0, 1)
    else:
        x = -1
        xp = -1

    print(f"\tt\t{t}")
    print(f"\tx\t{x if x > -1 else '-'}")
    print()
    print(f"\tt'\t{tp}")
    print(f"\tx'\t{xp if xp > -1 else '-'}")
    print()

    if failed:
        score = 0
    else:
        if approx(tp, 0) or approx(xp, 0):
            score = 0
        elif approx(tp, 1) and approx(xp, 1):
            score = 100
        else:
            score = 49 + 50 * math.sqrt(tp * xp)

    print(f"\tScore\t{score}{' (yay!)' if score == 100 else ''}")
    print()
