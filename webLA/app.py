from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def lexical_analysis(code):
    result = []
    keywords = {'int', 'for', 'if', 'else', 'while', 'return', 'system.out.println'}  
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        index = 0
        while index < len(line):
            token_detected = False
            for keyword in keywords:
                if line[index:].startswith(keyword) and (index + len(keyword) == len(line) or not line[index + len(keyword)].isalnum()):
                    result.append((line_number, index, 'Palabra reservada', keyword))
                    index += len(keyword)
                    token_detected = True
                    break
            if token_detected:
                continue

            char = line[index]
            if char in [';', '{', '}', '(', ')']:
                tipo = 'Punto y coma' if char == ';' else 'Llave' if char in ['{', '}'] else 'Paréntesis'
                result.append((line_number, index, tipo, char))
                index += 1
            elif char.isdigit():
                result.append((line_number, index, 'Número', char))
                index += 1
            else:
                index += 1
    return result

def syntactic_analysis(code):
    result = []
    correct_keyword = 'system.out.println'
    keywords = {'for', 'if', 'else', 'while', 'return'}  
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if stripped_line.startswith('system.out.'):
            if stripped_line.startswith(correct_keyword):
                result.append((line_number, correct_keyword, True))
            else:
                result.append((line_number, stripped_line.split('(')[0], False))
        elif 'system' in stripped_line or '.out' in stripped_line:
            result.append((line_number, stripped_line.split('(')[0], False))
        else:
            tokens = stripped_line.split()
            for token in tokens:
                if token in keywords:
                    result.append((line_number, token.capitalize(), True))
                elif any(keyword in token for keyword in keywords):
                    result.append((line_number, token.capitalize(), False))
                    break
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ""
    lexical_result = []
    syntactic_result = []
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                code = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            code = request.form['code']
        else:
            return "No file selected or code provided"
        
        lexical_result = lexical_analysis(code)
        syntactic_result = syntactic_analysis(code)
        
    return render_template_string(open("templates/index.html").read(), code=code, lexical_result=lexical_result, syntactic_result=syntactic_result)

if __name__ == '__main__':
    app.run(debug=True)
