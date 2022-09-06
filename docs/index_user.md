# Documentação de Usuário

Plataforma de Desafios de Design de Software

## <u>Getting Started</u>

- Rode o seguinte comando no terminal:

```
pip install -r requirements.txt
```

- Crie um arquivo `users.csv` e adicione ao seu conteúdo a seguinte estrutura:

```
<seu_nome>,<seu_cargo>
```

- Crie um arquivo `createdb.py` e adicione ao seu conteúdo a seguinte estrutura:

```
import sqlite3

with open('quiz.sql', 'r') as sql_file:
    sql_script = sql_file.read()

def createDb():
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    createDb()
```

- Rode `createdb.py`
- Rode `useradd.py`
- Rode `softdes.py`

## <u>Project Layout</u>

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
