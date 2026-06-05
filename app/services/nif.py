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
        url = f"https://consulta.edgarsingui.ao/consultar/{nif}"
        try:
            resposta = requests.get(url, timeout=15)
            if resposta.status_code == 200:
                try:
                    dados_ext = resposta.json()
                    if dados_ext.get("error") is False:
                        nome = dados_ext.get("name", nome)
                        endereco = dados_ext.get("endereco", endereco)
                    else:
                        raise HTTPException(status_code=400, detail="O NIF informado não foi encontrado ou é inválido.")
                except Exception:
                    # Se não for JSON, a API do Edgar Singui provavelmente devolveu a página HTML de erro (NIF não encontrado)
                    raise HTTPException(status_code=400, detail="O NIF informado não foi encontrado ou é inválido.")
            elif resposta.status_code in (400, 404, 422):
                raise HTTPException(status_code=400, detail="O NIF informado é inválido ou não existe no registo de Angola.")
            else:
                # Se a API estiver em baixo (500, etc), não bloqueamos o registo temporariamente
                nome = "Pendente de Validação"
                endereco = "Angola"
        except requests.exceptions.RequestException:
            # Se der timeout ou erro de rede a contactar a API, permitimos o registo
            nome = "Pendente de Validação"
            endereco = "Angola"
            
    # Validação para Empresa (NIF numérico de 10 dígitos)
    elif re.match(r"^\d{10}$", nif):
        tipo_nif = "Empresa / Entidade Coletiva"
        nome = "Empresa a Registar"
        endereco = "Endereço da Empresa"
    else:
        raise HTTPException(status_code=400, detail="Formato de NIF inválido.")
        
    return nome, endereco, tipo_nif, nif
