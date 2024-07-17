# test_minha_classe.py
import unittest
from db_config import *


class db_config_test(unittest.TestCase):

    def test_criar_tabela(self):
        print("1 Execunta teste de criao de tabela")
        create_table()
        self.assertEqual(1, 1)

    def test_criar_configuracao(self):
        print("2 Teste de criar configuracao")
        set("campo_teste", 123, "teste")
        set("campo_teste_outro", 456, "teste")
        self.assertEqual(1, 1)

    def test_pegar_configuracao(self):
        print("3 Teste de ler configuracao")
        campo = get("campo_teste")
        self.assertEqual(campo, "123")

    def test_pegar_tipo(self):
        print("3 Teste de ler configuracao tipo")
        campos = get_tipo("teste")
        self.assertEqual(campos["campo_teste"], "123")
        self.assertEqual(campos["campo_teste_outro"], "456")


if __name__ == "__main__":
    unittest.main()
