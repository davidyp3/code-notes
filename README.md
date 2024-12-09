# Code Notes

Uma aplicação web para salvar e organizar snippets de código de programação.

## Funcionalidades

- Salvar snippets de código com título, descrição e linguagem
- Suporte para várias linguagens de programação (Python, JavaScript, HTML, CSS, SQL, Java)
- Highlight de sintaxe automático
- Interface moderna e responsiva
- Fácil organização e busca de códigos

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Crie um ambiente virtual Python (recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # No Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

5. Acesse a aplicação no navegador: http://localhost:5000

## Como usar

1. Preencha o formulário com:
   - Título da nota
   - Linguagem de programação
   - Descrição (opcional)
   - Código

2. Clique em "Salvar Nota" para adicionar à sua coleção

3. Para excluir uma nota, clique no botão "Excluir" na nota desejada

## Tecnologias utilizadas

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Banco de dados: SQLite
- Highlight de código: Prism.js 