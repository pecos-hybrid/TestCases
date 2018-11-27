'''
This file serves a very specific purpose. In SU2 regression testing,
accuracy is checked by comparing stored values of the residuals against
the tested values.  Small changes to the numerics can result in small
but noticeable "errors." In order to get the regression tests to pass,
the test values must be updated to match the new numerics.  This can be
done by hand, but this script simplifies the process.  Just setup the
Travis CI log files as: serial.txt, serial_AD.txt, parallel.txt, and
parallel_AD.txt in the root of the SU2 directory and then run the script
from the root of the SU2 directory.  This script will output temporary
files like "TestCases/serial_regresion.py.tmp", which should be checked
and then copied over.
'''

def Replace(python_file, test_output_file):
    changes = []
    with open(test_output_file, 'r') as f:
        lines = f.read().splitlines()
        for i, line in enumerate(lines):
            if "ERROR" in line:
                old_test_vals = lines[i+2][20:]
                new_test_vals = lines[i+3][21:]
                CheckValues(old_test_vals, new_test_vals)
                changes.append((old_test_vals, new_test_vals))
        print("{0} replacements found.".format(len(changes)))
    with open(python_file, 'r') as infile:
        counter = 0
        with open(python_file + ".tmp", 'w') as outfile:
            for line in infile:
                new_line = line
                for change in changes:
                    if change[0].replace(" ", "") in line.replace(" ", ""):
                        new_line = line.replace(change[0], change[1])
                        counter += 1
                        changes.remove(change)
                outfile.write(new_line)
        print("{0} replacements made.".format(counter))


def CheckValues(old_values, new_values):
    old_values = [float(x) for x in old_values.split(',')]
    new_values = [float(x) for x in new_values.split(',')]
    for old, new in zip(old_values, new_values):
        if (old > 1E-6):
            error = abs((new - old)/old)
            if error > 0.001:
                print("Error with value: {0}, {1}".format(old, new))
                exit()


Replace("TestCases/serial_regression.py", "serial.txt")
Replace("TestCases/parallel_regression.py", "parallel.txt")
Replace("TestCases/serial_regression_AD.py", "serial_AD.txt")
Replace("TestCases/parallel_regression_AD.py", "parallel_AD.txt")
