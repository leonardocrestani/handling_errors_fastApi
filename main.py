# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from usuarios.usuarios import router as usuarios_router
from produtos.produtos import router as produtos_router

app = FastAPI()

# Inclui as rotas do modulo de usuarios
app.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])

# Inclui as rotas do modulo de produtos
app.include_router(produtos_router, prefix="/produtos", tags=["produtos"])

# Criacao de handler personalizado para excecoes do tipo HttpException
# Este handler serve para modificar o retorno e manipular as excecoes http apos serem chamadas
# Dentro dele e possivel utilizar logicas para os parametros recebidos para devolver ao usuario
@app.exception_handler(HTTPException)
async def http_excecao_customizada(request: Request, exc: HTTPException):
    # O parametro exc contem as informacoes da excecao que foi lancada (possui as propriedades passadas a ela)
    status_code = exc.status_code
    detail = exc.detail
    headers = exc.headers

    # Personalize a resposta
    content = {"mensagem": f"{detail}", "statusCode": f"{status_code}"}

    # Adiciona os headers na reposta apenas se eles existirem a resposta
    # Algumas funcoes podem mandar headers de erros necessarios quando chamado o HttpException
    if headers is not None:
        content["headers"] = headers
    return JSONResponse(status_code=status_code, content=content)

# Criacao de handler personalizado para excecoes do tipo RequestValidationError
# Este handler serve para modificar o retorno e manipular as excecoes de validacoes de o objetos da requisicao
@app.exception_handler(RequestValidationError)
async def excecao_validacao(request: Request, exc: RequestValidationError):
    # Converte os erros de validacao em um formato mais amigavel e os campos em portugues
    errors = [
        {
            "tipo": error["type"],
            "campo": error["loc"],
            "mensagem": error["msg"]
        }
        for error in exc.errors()
    ]
    # exc.errors() e um metodo que serve para retornar a lista de erros de validacao pois podemos ter mais de um erro de validacao na mesma chamada
    # Para cada erro ele monta a nova mensagem

    # Retorna uma resposta JSON com os dados pegos do erro e modificados
    return JSONResponse(
        status_code=422,
        content={"mensagem": "Erro de validação da requisição", "erros": errors},
    )

@app.exception_handler(Exception)
async def excecao_generica(request, exc):
    # Excecao customizada para casos onde acontecer um erro nao tratado
    # Retornar erro 500 interno
    return JSONResponse(
        status_code=500,
        content={"mensagem": "Internal Server Error"},
    )