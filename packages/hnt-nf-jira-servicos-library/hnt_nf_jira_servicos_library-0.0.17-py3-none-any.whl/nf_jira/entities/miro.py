from typing import Optional
from pydantic import BaseModel

from .dados_basicos_miro import DadosBasicosMiro
from .referencia_pedido import ReferenciaPedido
from .detalhe import Detalhe
from .sintese_miro import SinteseMiro

class Miro(BaseModel):
    dados_basicos: DadosBasicosMiro
    referencia_pedido: Optional[ReferenciaPedido] = None
    detalhe: Detalhe
    sintese: SinteseMiro