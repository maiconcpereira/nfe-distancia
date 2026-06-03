import xml.etree.ElementTree as ET
import requests
import sys
import time
from pathlib import Path


NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}


def parse_nfe_xml(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    inf_nfe = root.find('.//nfe:infNFe', NS)
    if inf_nfe is None:
        raise ValueError("Estrutura de NF-e não encontrada no XML.")

    def get_text(node, path):
        el = node.find(path, NS)
        return el.text.strip() if el is not None and el.text else ''

    emit = inf_nfe.find('nfe:emit', NS)
    if emit is None:
        raise ValueError("Dados do emitente não encontrados.")
    end_emit = emit.find('nfe:enderEmit', NS)

    dest = inf_nfe.find('nfe:dest', NS)
    if dest is None:
        raise ValueError("Dados do destinatário não encontrados.")
    end_dest = dest.find('nfe:enderDest', NS)

    def extrair(node_pai, prefix):
        return {
            'nome':      get_text(node_pai, f'nfe:xNome'),
            'cnpj':      get_text(node_pai, 'nfe:CNPJ') or get_text(node_pai, 'nfe:CPF'),
            'logradouro':get_text(prefix,   'nfe:xLgr'),
            'numero':    get_text(prefix,   'nfe:nro'),
            'complemento':get_text(prefix,  'nfe:xCpl'),
            'bairro':    get_text(prefix,   'nfe:xBairro'),
            'municipio': get_text(prefix,   'nfe:xMun'),
            'uf':        get_text(prefix,   'nfe:UF'),
            'cep':       get_text(prefix,   'nfe:CEP'),
        }

    return {
        'emitente':     extrair(emit, end_emit),
        'destinatario': extrair(dest, end_dest),
    }


def geocodificar(dados: dict) -> tuple:
    """
    Estratégia em cascata:
      1. Endereço completo (logradouro + número + município + UF + CEP)
      2. Endereço sem número
      3. Somente CEP
      4. Logradouro + município + UF
      5. Marco zero da cidade (praça central / prefeitura / câmara)
      6. Só município + UF  (último recurso)
    Retorna: (lat, lon, display_name, nivel_usado)
    """
    headers = {'User-Agent': 'nfe-distancia-app/1.0'}
    rua  = dados.get('logradouro', '').strip()
    num  = dados.get('numero', '').strip()
    mun  = dados.get('municipio', '').strip()
    uf   = dados.get('uf', '').strip()
    cep  = dados.get('cep', '').strip()

    # Remove zeros à esquerda do CEP e adiciona hífen se necessário
    cep_fmt = cep.zfill(8)
    if len(cep_fmt) == 8:
        cep_fmt = f"{cep_fmt[:5]}-{cep_fmt[5:]}"

    tentativas = []

    # 1. Endereço completo
    if rua and num and mun and uf and cep:
        tentativas.append((
            f"{rua}, {num}, {mun}, {uf}, {cep_fmt}, Brasil",
            "endereço completo"
        ))

    # 2. Endereço sem número
    if rua and mun and uf:
        tentativas.append((
            f"{rua}, {mun}, {uf}, Brasil",
            "logradouro sem número"
        ))

    # 3. Somente CEP
    if cep:
        tentativas.append((
            f"{cep_fmt}, Brasil",
            "CEP"
        ))

    # 4. Logradouro + município + UF (sem CEP)
    if rua and mun and uf:
        tentativas.append((
            f"{rua}, {mun}, {uf}, Brasil",
            "logradouro + município"
        ))

    # 5. Marco zero: praça central / prefeitura
    if mun and uf:
        tentativas.append((
            f"Praça Central, {mun}, {uf}, Brasil",
            "marco zero (praça central)"
        ))
        tentativas.append((
            f"Prefeitura Municipal de {mun}, {uf}, Brasil",
            "marco zero (prefeitura)"
        ))
        tentativas.append((
            f"Câmara Municipal de {mun}, {uf}, Brasil",
            "marco zero (câmara municipal)"
        ))

    # 6. Só município + UF
    if mun and uf:
        tentativas.append((
            f"{mun}, {uf}, Brasil",
            "município"
        ))

    for i, (query, nivel) in enumerate(tentativas):
        if i > 0:
            time.sleep(1)  # Respeita limite do Nominatim (1 req/s)
        try:
            resp = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'br'},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
            if results:
                return (
                    float(results[0]['lat']),
                    float(results[0]['lon']),
                    results[0]['display_name'],
                    nivel,
                )
        except Exception:
            continue

    raise ValueError(
        f"Não foi possível localizar '{mun}/{uf}' mesmo após todas as tentativas."
    )


def calcular_rota(lat1, lon1, lat2, lon2) -> dict:
    url = f'http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}'
    resp = requests.get(url, params={'overview': 'false'}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if data.get('code') != 'Ok':
        raise ValueError(f"Erro OSRM: {data.get('code')}")
    rota   = data['routes'][0]
    dist_m = rota['distance']
    dur_s  = rota['duration']
    dist_txt = f"{dist_m/1000:.1f} km" if dist_m >= 1000 else f"{dist_m:.0f} m"
    h, m = int(dur_s // 3600), int((dur_s % 3600) // 60)
    dur_txt = f"{h}h {m}min" if h > 0 else f"{m} min"
    return {'distancia_texto': dist_txt, 'distancia_metros': dist_m, 'duracao_texto': dur_txt}


def calcular_distancia_nfe(xml_path: str) -> None:
    print(f"\n{'='*62}")
    print("  CALCULADORA DE DISTÂNCIA - NF-e")
    print("  OpenStreetMap + OSRM  |  100% gratuito, sem API Key")
    print(f"{'='*62}\n")

    print(f"📄 Lendo XML: {xml_path}")
    dados = parse_nfe_xml(xml_path)
    emit  = dados['emitente']
    dest  = dados['destinatario']

    print(f"\n🏭 EMITENTE     : {emit['nome']}")
    print(f"   CNPJ         : {emit['cnpj']}")
    print(f"   Endereço     : {emit['logradouro']}, {emit['numero']} — {emit['municipio']}/{emit['uf']}")
    print(f"   CEP          : {emit['cep']}")

    print(f"\n📦 DESTINATÁRIO : {dest['nome']}")
    print(f"   CNPJ/CPF     : {dest['cnpj']}")
    print(f"   Endereço     : {dest['logradouro']}, {dest['numero']} — {dest['municipio']}/{dest['uf']}")
    print(f"   CEP          : {dest['cep']}")

    print("\n🌍 Geocodificando emitente...")
    lat1, lon1, end1, nivel1 = geocodificar(emit)
    print(f"   ✓ Resolvido via: {nivel1}")

    time.sleep(1)

    print("🌍 Geocodificando destinatário...")
    lat2, lon2, end2, nivel2 = geocodificar(dest)
    print(f"   ✓ Resolvido via: {nivel2}")

    print("\n🗺️  Calculando rota (OSRM)...")
    resultado = calcular_rota(lat1, lon1, lat2, lon2)

    print(f"\n{'='*62}")
    print("  RESULTADO")
    print(f"{'='*62}")
    print(f"  📍 Origem   : {end1}")
    if nivel1 != "endereço completo":
        print(f"             ⚠ Aproximado via: {nivel1}")
    print(f"  📍 Destino  : {end2}")
    if nivel2 != "endereço completo":
        print(f"             ⚠ Aproximado via: {nivel2}")
    print(f"\n  📏 Distância : {resultado['distancia_texto']}")
    print(f"  ⏱️  Duração   : {resultado['duracao_texto']} (de carro)")
    print(f"{'='*62}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python app.py <arquivo_nfe.xml>")
        sys.exit(1)
    xml_arquivo = sys.argv[1]
    if not Path(xml_arquivo).exists():
        print(f"Erro: arquivo '{xml_arquivo}' não encontrado.")
        sys.exit(1)
    try:
        calcular_distancia_nfe(xml_arquivo)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
