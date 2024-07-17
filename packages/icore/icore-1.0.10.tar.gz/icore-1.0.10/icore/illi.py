import requests
from datetime import datetime, timedelta, timezone
from app.config import Configuracao
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
import json

from app.internal.icore import icore
from app.internal.db_config import get


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

erro_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credencial Inválida",
    headers={"WWW-Authenticate": "Bearer"},
)
config = Configuracao()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class illi(icore):

    #
    #
    #
    # funcao para autenticar o usuario
    async def autenticar(self, usuario, senha):
        auth_url = f"{config.illi_base_url}/illi/autenticar"
        payload = {"login": usuario, "senha": senha}

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "(compatible; illiSoftware/1.0.0;ios)",
        }
        res = requests.post(auth_url, data=payload, headers=headers).json()
        if not res["success"]:
            erro_token
        else:
            if not res["xss"]:
                erro_token

        usuarioData = {"usuario": usuario, "xss": res["xss"]}
        return self.set_token(usuarioData)

    #
    #
    #
    #
    # codificar o token
    def set_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    #
    #
    #
    #
    # funcao para pegar o token decodificado
    def get_token(token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise erro_token

    #
    #
    #
    #
    #
    # funcao para pegar os dados do usuario
    async def get_sessao(self, token):
        url = f"{config.illi_base_url}/usuario/usuario/ijson/sessao"
        headers = {
            "User-Agent": "(compatible; illiSoftware/1.0.0;ios)",
            "content-type": "application/json",
            "xss": self.get_token(token)["xss"],
        }
        response = requests.post(url, headers=headers)
        print(response.text)
        try:
            ret = response.json()
            return ret
        except json.JSONDecodeError:
            print("Retornno Invalido")

    #
    #
    #
    #
    #
    # sair
    async def remover_sessao(self, token):
        url = f"{config.illi_base_url}/illi/destroy_session"
        headers = {
            "User-Agent": "(compatible; illiSoftware/1.0.0;ios)",
            # "content-type": "application/json",
            "xss": self.get_token(token)["xss"],
        }
        response = requests.post(url, headers=headers)
        return response.text

    #
    #
    #
    #
    #
    # rodar teste
    def rodar(self):
        print("Rodando")
        self.query("selet * from aqui")
        return

    # async def req(self, token):
    #     url = f"{config.illi_base_url}/illi/ijson/getSession"
    #     print(url)

    #     headers = {
    #         "User-Agent": "(compatible; illiSoftware/1.0.0;ios)",
    #         "content-type": "application/json",
    #         "xss": self.get_token(token)["xss"],
    #     }
    #     response = requests.post(url, headers=headers)
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         print(f"Error: {response.status_code}")
