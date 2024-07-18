import sys

from saphira import *

project = sys.argv[1]
stdin_input = []
for line in sys.stdin.readlines():
    stdin_input.append(line.strip())
test_name = stdin_input[0]
stdin_input = stdin_input[1:]
stdin_input_str = '\n'.join(stdin_input)
req, s3_link = save_manual_test_input(project, test_name, stdin_input_str)
update_test_status(project, req, '[FAILING]' not in stdin_input_str, test=s3_link)