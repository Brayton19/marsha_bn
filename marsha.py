import argparse
import asyncio
import os
import time

import autopep8
import openai

from llm import gpt_func_to_python, lint_and_fix_files, test_and_fix_files, prettify_time_delta
from parse import write_files_from_markdown

# Set up OpenAI
openai.organization = os.getenv('OPENAI_ORG')
openai.api_key = os.getenv('OPENAI_SECRET_KEY')

# Parse the input arguments (currently only one, the file to compile
parser = argparse.ArgumentParser(
    prog='marsha',
    description='Marsha AI Compiler',
)
parser.add_argument('source')
parser.add_argument('-d', '--debug', action='store_true', help='Turn on debug logging')
args = parser.parse_args()


def autoformat_files(files):
    for file in files:
        f = open(file, 'r')
        before = f.read()
        f.close()
        after = autopep8.fix_code(before)
        f = open(file, 'w')
        f.write(after)
        f.close()


async def main():
    t1 = time.time()
    print('Generating Python code...')
    f = open(args.source, 'r')
    func = f.read()
    f.close()
    files = write_files_from_markdown(await gpt_func_to_python(func))
    if args.debug:
        for file in files:
            print(file)
            f = open(file, 'r')
            print(f.read())
            f.close()
            print()
    print('Parsing generated code...')
    await lint_and_fix_files(files)
    if args.debug:
        for file in files:
            print(file)
            f = open(file, 'r')
            print(f.read())
            f.close()
            print()
    print('Verifying and correcting generated code...')
    await test_and_fix_files(func, files)
    if args.debug:
        for file in files:
            print(file)
            f = open(file, 'r')
            print(f.read())
            f.close()
            print()
    print('Formatting code...')
    autoformat_files(files)
    if args.debug:
        for file in files:
            print(file)
            f = open(file, 'r')
            print(f.read())
            f.close()
            print()
    t2 = time.time()
    print(f'Done! Total time elapsed: {prettify_time_delta(t2 - t1)}')


asyncio.run(main())
