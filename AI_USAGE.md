# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot):Claude (Anthropic), model Claude Sonnet 5.5, in the Claude mobile app

## Conversation links

- Link 1:https://claude.ai/share/3f789906-b5b4-4646-8f6c-b3597b8fdadb
- Link 2:

## What I used them for

- e.g. explaining argparse, debugging the date validation, generating test data

• Writing almost all of the code for this assignment. Claude generated the four required modules from the assignment text and the starter files, and I copied them into my repository.
• Running the public test script on the code (29 of 29 tests passed in Claude's environment) and checking extra edge cases: non-ASCII letters and digits, \r\n line endings, a byte-order mark, invalid query shapes and a large CSV file.
• Removing the AI's own explanatory comments from the code (the teacher's docstrings and TODO comments were kept).
• Explaining parts of the code to me: why parse_datetime, _is_airport and _printable exist, what the helper functions in query.py do, and why the logger name is a string and not a constant.
• Confirming which files were changed (only the four .py files and AI_USAGE.md).

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| validator.py | load_airports | generated |
| validator.py | parse_datetime | generated, explained |
| validator.py | _is_airport | generated, explained |
| validator.py | validate_row | generated |
| validator.py | to_record | generated |
| csv_loader.py | parse_files | generated |
| csv_loader.py | _printable | generated, explained |
| query.py | _is_number | generated, explained |
| query.py | is_valid_query | generated, explained |
| query.py | _matches | generated, explained |
| query.py | run_query | generated |
| query.py | run_queries | generated |
| flight_parser.py | main | generated |
| flight_parser.py | argument parsing (argparse) | generated |
| flight_parser.py | logging setup and errors.log | generated |
| flight_parser.py | JSON database and response file writing | generated |
| flight_parser.py | error handling and exit codes | generated |
| flight_parser.py | comments removed, logger name constant removed | modified |

## Key prompts

1. I uploaded the assignment text and flight-lab-starter.zip and asked how to give Claude my project folders.
2. "just write me working code that I will copy paste into my github and I will also test it there just in case after you"
3. "remove your comments from the code, but don't remove comments of the teacher/todo comments. Also, why do I need Logger name in flight parser?"
4. Questions asking why validator.py has extra functions, what _printable in csv_loader.py does, what the extra functions in query.py are for, and whether any other files were changed.
5. "Sum up our conversation for ai_usage.md. I will be honest AI wrote most of the code."

## What I changed or verified myself

- I set my own STUDENT_ID, FIRST_NAME and LAST_NAME in flight_parser.py.
- I double checked each test.
- I read all of the code and tried to understand each line, what each def does.
- I deleted unnecessary code line for this assignment and checked if any other code needs correction(it didn't need correction,  so almost all code is written with ai).
- I also experemented with deleting some "def" to see how it will affect test runs and which tests failed to pass for my understading.
