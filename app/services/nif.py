import requests
import re
from fastapi import HTTPException

def consultar_nif_externo(nif: str):
    """
    Consulta a API externa para validar o NIF e obter dados de identidade.
    Retorna (nome, endereco, tipo_nif) ou levanta HTTPException em caso de erro.
    """
    nif = nif.replace(" ", "").replace(".", "").strip().upper()
    
    nome = "Desconhecido"
    endereco = "Desconhecido"
    tipo_nif = "Desconhecido"
    
    # Validação para Pessoa Singular (NIF angolano com letras no fim ou similar)
    if re.match(r"^\d{9}[A-Z]{2}\d{3}$", nif):
        tipo_nif = "Pessoa Singular"
        url = f"https://identity-lookup.onrender.com/v3/identities/personal/{nif}"
        try:
            resposta = requests.get(url, timeout=15)
            if resposta.status_code == 200:
                dados_ext = resposta.json()
                nome = dados_ext.get("fullName", nome)
                endereco = dados_ext.get("address", endereco)
            else:
                raise HTTPException(status_code=400, detail="Não foi possível encontrar dados para este BI na base nacional.")
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Erro de comunicação com a base nacional.")
            
    # Validação para Empresa (NIF numérico de 10 dígitos)
    elif re.match(r"^\d{10}$", nif):
        tipo_nif = "Empresa / Entidade Coletiva"
        nome = "Empresa a Registar"
        endereco = "Endereço da Empresa"
    else:
        raise HTTPException(status_code=400, detail="Formato de NIF inválido.")
        
    return nome, endereco, tipo_nif, nif
