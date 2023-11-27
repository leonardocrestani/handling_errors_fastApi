# products.py
from fastapi import APIRouter, HTTPException, Depends
from usuarios.usuarios import busca_usuario_email
from util.jwt import verifica_token
from util.validaFuncao import valida_funcao

from pydantic import BaseModel

router = APIRouter()

# Lista para armazenar os produtos e simular um banco de dados
produtos = [
    {"id": 1, "name": "Cimento", "preco": 20.0, "quantidade": 100},
    {"id": 2, "name": "Tijolos", "preco": 0.5, "quantidade": 500},
    {"id": 3, "name": "Tinta", "preco": 30.0, "quantidade": 50},
]

# Cria um modelo para o body de uma requisicao neste caso vai ser utilizado na compra de produto
class BodyProdutos(BaseModel):
    email: str
    quantidade: float = None

# Rota para buscar todos os produtos
# Usuario deve estar autenticado e ter a funcao validada
@router.get("", dependencies=[Depends(verifica_token), Depends(valida_funcao)])
async def busca_produtos():
    return {"Produtos": produtos}

# Rota para comprar um produto
@router.post("/comprar_produto/{id_produto}", dependencies=[Depends(verifica_token)])
async def comprar_produto(id_produto: int, body: BodyProdutos):
    # Buscar o produto pelo ID
    produto = None
    for produto_indice in produtos:
        if produto_indice["id"] == id_produto:
            produto = produto_indice
            break
    
    # Se produto nao for encontrado retorna o erro 404 (not found) para indicar que o produto de ID informado nao foi encontrado
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verifica se possui estoque disponovel do pedido
    if produto["quantidade"] <= 0:
        raise HTTPException(status_code=400, detail=f"Produto {produto['name']} fora de estoque")

    # Busca usuario pelo email
    usuario = busca_usuario_email(body.email)
    
    # Verifica se o usuario tem saldo suficiente para comprar o produto
    if usuario["saldo"] < produto["preco"] * body.quantidade:
        # Se nao possuir saldo retorna erro 400 HttpException
        # Indica que a requisicao do cliente é invalida devido a uma condicaoo no lado do cliente nesse caso o saldo insuficiente
        raise HTTPException(status_code=400, detail="Saldo insuficiente para comprar o produto")

    # Logica para simular a compra reduz a quantidade disponivel de itens no estoque e subtrai o preco do saldo do usuario
    produto["quantidade"] -= body.quantidade
    usuario["saldo"] -= produto["preco"] * body.quantidade

    return {"message": f"Produto {produto['name']} comprado com sucesso. Saldo restante: {usuario['saldo']}"}

