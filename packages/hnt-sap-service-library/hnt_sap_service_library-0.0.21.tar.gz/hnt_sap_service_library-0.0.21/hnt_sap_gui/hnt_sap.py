import logging
import locale
from SapGuiLibrary import SapGuiLibrary
from dotenv import load_dotenv

from hnt_sap_gui.RPA_HNT_Constants import COD_LIBERACAO_BLOQUADO

from .common.session import sessionable
from .nota_fiscal.nota_pedido_transaction import NotaPedidoTransaction
from .nota_fiscal.fatura_transaction import FaturaTransaction
from .nota_fiscal.miro_transaction import MiroTransaction
from .nota_fiscal.liberacao_transaction import LiberacaoTransaction

logger = logging.getLogger(__name__)

class SapGui(SapGuiLibrary):
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, ('pt_BR.UTF-8'))
        load_dotenv()
        pass
    def format_float(self, value):
        return locale.format_string("%.2f", value)

    @sessionable
    def hnt_run_transaction(self, data):
        logger.info(f"enter execute run_hnt_transactions data:{data}")
        results = {
            "nota_pedido": None,
            "error": None
        }
        try:
            if 'nota_pedido' in data:
                tx_result_nota_pedido = NotaPedidoTransaction().execute(self, nota_pedido=data['nota_pedido'])
                results['nota_pedido'] = tx_result_nota_pedido

                tx_result_liberacao = LiberacaoTransaction().execute(self, results['nota_pedido'].codigo)
                results["liberacao"] = tx_result_liberacao
            
                if COD_LIBERACAO_BLOQUADO == tx_result_liberacao.codigo:
                    logger.info(f"leave execute hnt_run_transaction_miro result:{', '.join([str(results[obj]) for  obj in results])}")
                    return results
            
                results["miro"] = MiroTransaction().execute(self, data['miro'], results['nota_pedido'].codigo)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute run_hnt_transactions result:{', '.join([str(results[obj]) for obj in results])}")
        return results
    
    @sessionable
    def hnt_run_transaction_FV60(self, data):
        results = {
            "fatura": None,
            "error": None
        }
        try:
            results["fatura"] = FaturaTransaction().execute(self, data)
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute run_hnt_transactions result:{', '.join([str(results[obj]) for obj in results])}")
        return results

    @sessionable
    def hnt_run_transaction_ME21N(self, data):
        logger.info(f"enter execute run_hnt_transactions data:{data}")
        results = {
            "nota_pedido": None,
            "error": None
        }
        try:
            if 'nota_pedido' in data:
                tx_result_nota_pedido = NotaPedidoTransaction().execute(self, nota_pedido=data['nota_pedido'])
                results['nota_pedido'] = tx_result_nota_pedido
        except Exception as ex:
            logger.error(str(ex))
            results["error"] = str(ex)
        logger.info(f"leave execute run_hnt_transactions result:{', '.join([str(results[obj]) for obj in results])}")
        return results
    
    @sessionable
    def hnt_run_transaction_miro(self, numero_pedido, data):
        logger.info(f"enter execute run_hnt_transactions data:{data}")
        results = {
            "miro": None,
            "liberacao": None,
            "error": None
        }

        try:
            tx_result_liberacao = LiberacaoTransaction().execute(self, numero_pedido)
            results["liberacao"] = tx_result_liberacao
            
            if COD_LIBERACAO_BLOQUADO == tx_result_liberacao.codigo:
                logger.info(f"leave execute hnt_run_transaction_miro result:{', '.join([str(results[obj]) for  obj in results])}")
                return results
            
            results["miro"] = MiroTransaction().execute(self, data, numero_pedido)

        except Exception as e:
            logger.error(str(e))
            results["error"] = str(e)

        logger.info(f"leave execute hnt_run_transaction_miro result:{', '.join([str(results[obj]) for obj in results])}")
        return results