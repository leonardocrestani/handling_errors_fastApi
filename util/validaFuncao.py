from fastapi import Depends, HTTPException
from usuarios.usuarios import busca_usuario_email
from util.jwt import verifica_token
def valida_funcao(data: dict = Depends(verifica_token)):
  usuario = busca_usuario_email(data)
  if usuario["funcao"] != "admin":
    raise HTTPException(
      status_code=403,
      detail="Acesso proibido para o usuarios que nao sao admin"
    )