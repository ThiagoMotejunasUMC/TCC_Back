from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/viacep", tags=["ViaCEP"])

@router.get("/{cep}")
async def buscar_cep(cep: str):
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        raise HTTPException(status_code=400, detail="CEP inválido")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao consultar ViaCEP")
    data = response.json()
    if "erro" in data:
        raise HTTPException(status_code=404, detail="CEP não encontrado")
    return {
        "cep": data.get("cep"),
        "logradouro": data.get("logradouro"),
        "bairro": data.get("bairro"),
        "cidade": data.get("localidade"),
        "estado": data.get("uf")
    }