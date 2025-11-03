GUIA DE CONFIGURAÇÃO DO AMBIENTE DE DESENVOLVIMENTO:

Este guia explica os passos necessários para configurar o ambiente de desenvolvimento local, garantindo que todos os membros da equipe usem as mesmas dependências. O projeto utiliza um ambiente virtual Python (venv).

1. PRÉ-REQUISITOS

Certifique-se de ter os seguintes softwares instalados:

Python 3.x

Git

2. CLONAGEM DO REPOSITÓRIO

Clone o projeto para sua máquina local:

git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_PROJETO>


3. CRIAÇÃO E ATIVAÇÃO DO AMBIENTE VIRTUAL (venv)

3.1. Criação do Ambiente Virtual

Execute este comando no terminal para criar o diretório venv:

python -m venv venv


(Nota: Use python3 -m venv venv se o seu sistema exigir o comando python3.)

3.2. Ativação do Ambiente Virtual

Você deve ativar o ambiente virtual antes de instalar pacotes. Escolha o comando apropriado para o seu sistema:

Sistema Operacional

Comando de Ativação

Windows (PowerShell)

.\venv\Scripts\Activate.ps1

Windows (Prompt de Comando/CMD)

venv\Scripts\activate.bat

macOS / Linux (Bash/Zsh)

source venv/bin/activate

Após a ativação, você verá o prefixo (venv) no terminal.

4. INSTALAÇÃO DAS DEPENDÊNCIAS

Com o ambiente virtual ativo, instale todos os pacotes listados no requirements.txt:

pip install -r requirements.txt


5. EXECUTANDO A APLICAÇÃO (APLICATIVO DESKTOP)

Para iniciar o aplicativo de interface gráfica (GUI) usando PySide6:

python __main__.py


6. DICA PARA COLABORADORES: ATUALIZAR DEPENDÊNCIAS

Se você instalar um novo pacote com pip, use o comando a seguir (com o venv ativo) para atualizar o requirements.txt para a equipe:

pip freeze > requirements.txt


7. DESATIVAR O AMBIENTE

Para sair do ambiente virtual:

deactivate


🚀 GUIA DE CONTRIBUIÇÃO (FLUXO DE PULL REQUEST)

A branch principal (main) está protegida e exige revisão. Siga estes passos para que suas alterações sejam aceitas no projeto:

1. PREPARAÇÃO LOCAL

1.1. Atualize a Branch Principal:

Volte para a main:

git checkout main


Baixe as últimas alterações do GitHub:

git pull origin main


1.2. Crie sua Branch de Trabalho:

Crie uma branch específica para a sua tarefa (ex: feature/login, fix/erro-calculo):

git checkout -b nome-da-sua-branch


2. COMMIT LOCAL

2.1. Adicione os Arquivos:

Prepare os arquivos modificados para o commit:

git add .


2.2. Confirme as Alterações (Commit):

Crie um commit com uma mensagem clara:

git commit -m "feat: Adiciona formulario de login"


3. ENVIO PARA O GITHUB (PUSH)

3.1. Envie a Branch:

Suba sua nova branch para o GitHub:

git push -u origin nome-da-sua-branch


4. CRIAÇÃO E REVISÃO DA PULL REQUEST (PR)

4.1. Crie a PR:

Acesse o repositório no GitHub.

Use o botão "Compare & pull request" que aparecerá.

Preencha o título e a descrição da PR.

4.2. Aguarde a Revisão:

O responsável pelo projeto (o Proprietário) ou outro colaborador designado irá revisar o seu código.

Se for solicitada alguma alteração, faça os novos commits na sua branch local e envie novamente (git push). A Pull Request será automaticamente atualizada.

4.3. Mesclagem (Merge):

Após a aprovação, o código será mesclado na branch main.

5. LIMPEZA (OPCIONAL)

5.1. Volte para a Main:

Troque de volta para a branch principal:

git checkout main


5.2. Exclua a Branch Local:

Deleta a branch que acabou de ser mesclada:

git branch -d nome-da-sua-branch