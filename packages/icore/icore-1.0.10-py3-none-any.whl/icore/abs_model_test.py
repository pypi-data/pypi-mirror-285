# test_minha_classe.py
import unittest
import abs_model


class abs_model_test(unittest.TestCase):

    def test_saudacao(self):
        # print("Execunta teste de saudação")
        # Criar uma instância da classe
        _abs_model = abs_model.abs_model("db_illi")
        # Chamar o método a ser testado
        # resultado = objeto.saudacao()
        # # Verificar se o resultado está correto

        # print("Aqui")
        df = _abs_model.query("select * from stg_nfe_linx_illi limit 1000")
        print(df.head())
        # self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
