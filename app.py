from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Directory where CSV files are stored
CSV_FOLDER = 'questions'
app.config['CSV_FOLDER'] = CSV_FOLDER

@app.route('/')
def index():
    # List all CSV files in the 'questions' directory
    csv_files = [f for f in os.listdir(app.config['CSV_FOLDER']) if f.endswith('.csv')]
    return render_template('index.html', files=csv_files)

@app.route('/select_file/<filename>')
def select_file(filename):
    if filename not in os.listdir(app.config['CSV_FOLDER']):
        return redirect(url_for('index'))

    session['current_file'] = filename
    session['score'] = 0
    session['incorrect_questions'] = []

    return redirect(url_for('question', index=0))

@app.route('/question/<int:index>', methods=['GET', 'POST'])
def question(index):
    # Check if a file is selected
    if 'current_file' not in session:
        return redirect(url_for('index'))

    # Load the questions from the selected CSV file
    questions_df = pd.read_csv(os.path.join(app.config['CSV_FOLDER'], session['current_file']))

    if index >= len(questions_df):
        return redirect(url_for('result'))

    if request.method == 'POST':
        selected_option = request.form.get('option')
        correct_option = questions_df.iloc[index]['correctAns']

        if selected_option == correct_option:
            session['score'] = session.get('score', 0) + 1
        else:
            incorrect_questions = session.get('incorrect_questions', [])
            if index not in incorrect_questions:
                incorrect_questions.append(index)
            session['incorrect_questions'] = incorrect_questions

        next_index = index + 1
        if next_index >= len(questions_df):
            return redirect(url_for('result'))
        return redirect(url_for('question', index=next_index))

    question_data = questions_df.iloc[index]
    options = {
        'A': question_data['optionA'],
        'B': question_data['optionB'],
        'C': question_data['optionC'],
        'D': question_data['optionD']
    }
    return render_template('index.html', question=question_data, index=index, options=options)

@app.route('/result')
def result():
    # Load the questions from the selected CSV file
    questions_df = pd.read_csv(os.path.join(app.config['CSV_FOLDER'], session['current_file']))

    total_questions = len(questions_df)
    score = session.get('score', 0)
    incorrect_questions = session.get('incorrect_questions', [])

    return render_template('result.html', score=f"{score}/{total_questions}", incorrect_questions=incorrect_questions, questions_df=questions_df)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and file.filename.endswith('.csv'):
        filename = file.filename
        file.save(os.path.join(app.config['CSV_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('index'))
    else:
        flash('Allowed file types are .csv')
        return redirect(request.url)

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
