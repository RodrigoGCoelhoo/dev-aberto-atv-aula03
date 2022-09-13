# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: rauli
"""

from datetime import datetime
import sqlite3
import hashlib
import numbers
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth

DBNAME = './quiz.db'

def lambda_handler(event):
    """
    This function fetches content from mysql RDS instance
    """
    try:
        def not_equals(first, second):
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        code()

        test = []
        for index, _ in enumerate(args):
            if not f"desafio{ndes}" in locals():
                return f"Nome da função inválido. Usar 'def desafio{ndes}(...)'"

            if not_equals('desafio{ndes}(*arg)', resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except TypeError as error:
        return f"Função inválida. {error}"

def converte_data(orig):
    """
    Convert data into the right format
    """
    return orig[8:10]+'/'+orig[5:7]+'/'+orig[0:4]+' '+orig[11:13]+':'+orig[14:16]+':'+orig[17:]

def get_quizes(user):
    """
    Get all the quizzes data
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user in ['admin', 'fabioja']:
        cursor.execute("SELECT id, numb from QUIZ")
    else:
        cursor.execute(f"SELECT id, numb from QUIZ where release < '{formatted_date}'")

    info = cursor.fetchall()
    conn.close()
    return info

def get_user_quiz(user_id, quiz_id):
    """
    Get the user quizzes data
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sent,answer,result from USERQUIZ where \
                     userid = ? and quizid = ? order by sent desc", (user_id, quiz_id))
    info = cursor.fetchall()
    conn.close()
    return info

def set_user_quiz(userid, quizid, sent, answer, result):
    """
    Set the user quizzes data
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) \
                    values (?,?,?,?,?);", (userid, quizid, sent, answer, result))
    conn.commit()
    conn.close()

def get_quiz(quiz_id, user):
    """
    Get the quizze
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user in ['admin', 'fabioja']:
        cursor.execute("SELECT id, release, expire, problem, tests, results, \
                        diagnosis, numb from QUIZ where id = ?", (quiz_id))
    else:
        cursor.execute("SELECT id, release, expire, problem, tests, results, diagnosis, numb from \
                         QUIZ where id = ? and release < ?", (quiz_id, formatted_date))
    info = cursor.fetchall()
    conn.close()
    return info

def set_info(pwd, user):
    """
    Set info data
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()

def get_info(user):
    """
    Get all info data
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT pass from USER where user = '{user}'" )

    info = cursor.fetchall()
    print(info[0][0])
    conn.close()
    if len(info) == 0:
        return None
    return info[0][0]

auth = HTTPBasicAuth()

app = Flask(__name__, static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def main():
    """
    Main function data
    """
    msg = ''
    page = 1
    challenges = get_quizes(auth.username())
    sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST' and 'ID' in request.args:
        user_id = request.args.get('ID')
        quiz = get_quiz(id, auth.username())
        if len(quiz) == 0:
            msg = "Boa tentativa, mas não vai dar certo!"
            page = 2
            return render_template('index.html', username=auth.username(), \
                                   challenges=challenges, page=page, msg=msg)


        quiz = quiz[0]
        if sent > quiz[2]:
            msg = "Sorry... Prazo expirado!"

        requested_file = request.files['code']
        filename = './upload/{auth.username()}-{sent}.py'
        requested_file.save(filename)
        with open(filename,'r', encoding="utf-8") as infile:
            answer = infile.read()

        #lamb = boto3.client('lambda')
        args = {"ndes": user_id, "code": answer, "args": quiz[4], "resp": quiz[5], "diag": quiz[6]}

        #response = lamb.invoke(FunctionName="Teste", InvocationType='RequestResponse', \
        #Payload=json.dumps(args))
        #feedback = response['Payload'].read()
        #feedback = json.loads(feedback).replace('"','')
        feedback = lambda_handler(args)

        result = 'Erro'
        if len(feedback) == 0:
            feedback = 'Sem erros.'
            result = 'OK!'

        set_user_quiz(auth.username(), user_id, sent, feedback, result)


    if request.method == 'GET':
        if 'ID' in request.args:
            user_id = request.args.get('ID')
        else:
            user_id = 1

    if len(challenges) == 0:
        msg = "Ainda não há desafios! Volte mais tarde."
        page = 2
        return render_template('index.html', username=auth.username(), \
                               challenges=challenges, page=page, msg=msg)

    quiz = get_quiz(user_id, auth.username())

    if len(quiz) == 0:
        msg = "Oops... Desafio invalido!"
        page = 2
        return render_template('index.html', username=auth.username(), \
                               challenges=challenges, page=page, msg=msg)

    answers = get_user_quiz(auth.username(), user_id)

    return render_template('index.html', username=auth.username(), challenges=challenges, \
                            quiz=quiz[0], e=(sent > quiz[0][2]), answers=answers, page=page, \
                            msg=msg, expi = converte_data(quiz[0][2]))

@app.route('/pass', methods=['GET', 'POST'])
@auth.login_required
def change():
    """
    Main function data
    """
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        page = 1
        msg = ''
        if nova != repet:
            msg = 'As novas senhas nao batem'
            page = 3
        elif get_info(auth.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = 'A senha antiga nao confere'
            page = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), auth.username())
            msg = 'Senha alterada com sucesso'
            page = 3
    else:
        msg = ''
        page = 3

    return render_template('index.html', username=auth.username(), \
                            challenges=get_quizes(auth.username()), page=page, msg=msg)


@app.route('/logout')
def logout():
    """
    Function to logout the user
    """
    return render_template('index.html',p=2, msg="Logout com sucesso"), 401

@auth.get_password
def get_password(username):
    """
    Function to change users password
    """
    if username:
        return get_info(username)
    return None

@auth.hash_password
def hash_pw(password):
    """
    Function to hash the password
    """
    return hashlib.md5(password.encode()).hexdigest()

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=8080)
