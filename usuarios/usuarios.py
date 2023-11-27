# users.py
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta
from util.jwt import verifica_token, cria_access_token, TEMPO_EXPIRAR_TOKEN

from pydantic import BaseModel

router = APIRouter()

# Lista para armazenar os usuarios e simular um banco de dados
usuarios = []

# Cria um modelo para o body de uma requisicao neste caso vai ser utilizado na de deposito
# Este body que vai ser validado pelo RequestValidationError e devolver nosso erro presonalizado
class BodyDinheiro(BaseModel):
    valor: float = None

# Cria um modelo para o body de uma requisicao neste caso vai ser utilizado na de criacao de usuario
class BodyUsuario(BaseModel):
    email: str
    senha: str
    funcao: str

# Rota para criar um novo usuario
@router.post("/criar_usuario", status_code=201)
async def criar_usuario(body: BodyUsuario):
    # Teste para excecao nao tratada
    # aa = body["TESTE"]
    # Verifica se o email já está em uso
    for usuario in usuarios:
        if usuario["email"] == body.email:
            # Caso o usuario ja exista e devolvido um HttpException com o status de 409 (conflict)
            # Isto indica que a requisicao atual esta conflitando com um recurso ja no banco de dados
            # Tambem e devolvido um header personalizado que indica que usuario nao foi criado e esta informacao pode ser util para outras requisicao (exemplo)
            raise HTTPException(status_code=409, detail="Email já cadastrado", headers={"X-User-Created": False})

    # Cria um novo objeto com as novas informacoes apos serem validadas
    novo_usuario = {
        "email": body.email,
        "senha": body.senha,
        "funcao": body.funcao,
        "saldo": 0
    }

    # Adiciona o usuário ao array de usuarios que simula o banco
    usuarios.append(novo_usuario)

    # Adiciona o cabeçalho X-User-Created ao objeto headers
    headers = {"X-User-Created": True}

    # Adiciona o header ao objeto de retorno juntamente com o novo body
    novo_usuario_dict = novo_usuario
    novo_usuario_dict["headers"] = headers

    # Retorna o novo body e statusCode 201 (created)
    return novo_usuario_dict

# Rota para autenticacao e geracao de token se seguranca
@router.post("/login")
async def autenticacao(body: dict):
    # Atribui os campos recebido para validacao futura
    email = body.get("email")
    senha = body.get("senha")

    # Itera sobre os cada usuario na lista para encontrar o usuario com as credenciais corretas
    for usuairo in usuarios:
        # Verifica se email e senha estao corretos
        # Se o usuario estiver correto com email e senha vai poder ser gerado um token JWT para ele se autenticar em outras requisicoes
        if usuairo["email"] == email and usuairo["senha"] == senha:
            # Gera um token JWT com base no email do usuario
            tempo_restante_JWT = timedelta(minutes=TEMPO_EXPIRAR_TOKEN)
            access_token = cria_access_token(data={"sub": email}, expires_delta=tempo_restante_JWT)
            # Retorna sucesso na autenteicacao do usuario e o token na variavel access_token para posterior utilizacao
            return {"access_token": access_token, "token_type": "bearer"}

    # Se informacoes do usuario estiverem incorretas e lancado o HttpException de status 401 indicando que o usuario nao foi autenticado
    # Os dados do usuarios estao incorretos e o erro e devolvido
    headers = {"X-Error-Code": "INVALID_CREDENTIALS"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas", headers=headers)

# Rota para realizar um depósito na conta de um usuário autenticado
# Utilizando dependencia da funcao verify_token usuario precisar estar autenticado para fazer chamada a rota
@router.post("/deposito/{email}", dependencies=[Depends(verifica_token)])
async def deposito(email: str, body: BodyDinheiro):
    # Procura usuario na lista de usuarios para ver se ele existe
    usuario_encontrado = {}
    for usuario in usuarios:
        if usuario["email"] == email:
            usuario_encontrado = usuario
            break

    # Se usuario nao for encontrado retorna o erro 404 (not found) para indicar que usuario informado nao foi encontrado
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Valida se o valor do depósito é positivo
    # Se valor de deposito nao for maior que 0 o erro e devolvido (depositos so podem ser feitos com valor maior que 0)
    # Retorna status 400 de bad request (requisição mal formada os valores estao incorretos)
    if body.valor <= 0:
        raise HTTPException(status_code=400, detail="O valor do depósito deve ser positivo")

    # Realiza o deposito alterando valor do item saldo no objeto do usuario informado que foi encontrado
    usuario_encontrado["saldo"] = usuario_encontrado.get("saldo", 0) + body.valor

    return {"message": f"Depósito de {body.valor} realizado com sucesso. Novo saldo: {usuario_encontrado['saldo']}"}


# Funcaoo auxiliar para buscar um usuario pelo email
# Esta funcao pode ser utilizada em diversos locais da aplicacao
def busca_usuario_email(email: str):
    for usuario in usuarios:
        if usuario["email"] == email:
            return usuario
    raise HTTPException(status_code=404, detail="Usuário não encontrado")