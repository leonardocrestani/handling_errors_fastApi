# users.py
from fastapi import HTTPException
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta

# Chave secreta para gerar o token
SECRET_KEY = "testKey"

# Configurações do token
ALGORITMO = "HS256"
TEMPO_EXPIRAR_TOKEN = 60

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

# Função para verificar a validade do token recebido nas requisições
def verifica_token(token: str = Depends(oauth2_schema)):
    try:
        # Decodifica o token usando a chave secreta e o algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        # Pega o email do payload do token
        # Como o token foi gerado passando o email do usuario como parametro é possivel extrair ele na validacao
        email: str = payload.get("sub")
        # Verifica se conseguiu pegar o email do token se nao conseguir retorna erro de token invalido 401 nao autorizado
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
        return email
    # Trata excecao se a assinatura do token for inválida
    # Se token estiver fora do formato
    except jwt.InvalidSignatureError:
        raise HTTPException(
          status_code=401,
          detail="Assinatura inválida no token"
        )

# Funcao para criar um token de acesso
def cria_access_token(data: dict, expires_delta: timedelta):
    # Cria uma copia dos dados que vao ser codificados no token (neste explo vai receber o email do usuario)
    payload = data.copy()
    tempo_expiracao_token = datetime.utcnow() + expires_delta
    payload.update({"exp": tempo_expiracao_token})
    # Cria o token usando a chave secreta o algoritmo especificado e o body enviado
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)
    return token