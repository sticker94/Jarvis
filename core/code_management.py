# core/code_management.py

import ast
import os
import assist

def generate_code_from_description(description):
    prompt = f"Generate Python code that {description}. Wrap the code in <code> tags."
    response = assist.ask_question_memory(prompt)
    start_index = response.find('<code>') + len('<code>')
    end_index = response.find('</code>')
    code_content = response[start_index:end_index].strip()

    if code_content.startswith('```') and code_content.endswith('```'):
        code_content = code_content[3:-3].strip()
    return code_content

def update_code(description, filename):
    new_code = generate_code_from_description(description)
    with open(filename, 'w') as file:
        file.write(new_code)
    return f"Code updated in {filename}"

def create_file(description, filename):
    if not os.path.exists(filename):
        new_code = generate_code_from_description(description)
        with open(filename, 'w') as file:
            file.write(new_code)
        return f"File {filename} created successfully with functionality: {description}"
    else:
        return f"File {filename} already exists. Please choose a different name."

def check_syntax_errors(code):
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        lines = code.split('\n')
        while True:
            try:
                ast.parse('\n'.join(lines))
                break
            except SyntaxError as e:
                errors.append(f"Line {e.lineno}: {e.msg}")
                lines.pop(e.lineno - 1)
    return errors

def suggest_fixes_for_errors(errors, code):
    error_messages = "\n".join(errors)
    prompt = f"The following Python code has errors:\n\n{code}\n\nThe errors are:\n{error_messages}\n\nPlease provide a corrected version of the code. Wrap the code in <code> tags."
    response = assist.ask_question_memory(prompt)
    start_index = response.find('<code>') + len('<code>')
    end_index = response.find('</code>')
    fixed_code = response[start_index:end_index].strip()

    if fixed_code.startswith('```') and fixed_code.endswith('```'):
        fixed_code = fixed_code[3:-3].strip()
    return fixed_code

def check_and_fix_file(filename, recorder):
    with open(filename, 'r') as file:
        code = file.read()
    errors = check_syntax_errors(code)
    if errors:
        error_messages = "\n".join(errors)
        assist.TTS(f"Errors found in {filename}:\n{error_messages}")
        assist.TTS("Do you want to fix these errors?")
        confirmation = recorder.text().strip().lower()
        if "yes" in confirmation or "yeah" in confirmation or "sure" in confirmation:
            fixed_code = suggest_fixes_for_errors(errors, code)
            with open(filename, 'w') as file:
                file.write(fixed_code)
            return f"Errors in {filename} have been fixed."
        else:
            return f"Errors in {filename} were not fixed."
    else:
        return f"No errors found in {filename}."

def check_and_fix_project(recorder):
    results = []
    for filename in os.listdir():
        if filename.endswith(".py"):
            result = check_and_fix_file(filename, recorder)
            results.append(result)
    return "\n".join(results)
