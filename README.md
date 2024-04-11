# cs-145-scripts

Scripts for testing CS 145 2324B Programming Tasks. 

## What is it
<img width="431" alt="Screenshot 2024-02-19 at 2 15 40 PM" src="https://github.com/jproads/cs-145-scripts/assets/93178783/f9f6c2b5-5523-4248-a84f-520284c3a37b">

Runs tests on your `taskN.py`. Measures time-outs and output errors, and displays problematic test cases. Calculates your solution's performance. Total bits, average bits per message, x-value (formula given in each PT doc), and your score over 100.

The **number of tests** ran and **random seed** for each test program may be customized. Defaults are 100 tests and a random seed of `0xC0DEBABE`.

## How to use
1. For PT number `n` (`n = 0, 1`), download `test[n].py` and place in your `task[n]attachments` folder.
   - For PT2, download `test2.py` and `judgetool.pyc` and place in your `task2attachments` folder.
3. **Important:** In your terminal, navigate to `task[n]attachments/` and run `python3 test[n].py -h` to see the available options for running the script.
   - To check if your PT2 solution is valid, run a single test via `python test2.py -n 1`. Running the full 50 tests can take a while, and is recommended only for checking your score.
## Extra
Contributions are welcome! Raise an issue or a PR and I'll get to it ASAP.

## Contributors
jproads, daryll-ko, Ulyzses

*Released with permission from Sir Kevin and Sir Jem.*
