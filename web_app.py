"""
Interface Web — Calculadora de Distância NF-e
Modos: upload de XML  OU  consulta por CNPJ
100% gratuito · sem API Key · ReceitaWS + OpenStreetMap + OSRM
Instalar : pip install flask requests
Executar : python web_app.py  →  http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template_string
import xml.etree.ElementTree as ET
import requests
import time
import re

app = Flask(__name__)
NS  = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Distância NF-e</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0f1117;--surface:#1a1d27;--border:#2a2d3a;--accent:#00d4aa;--text:#e2e4ec;--muted:#6b7080;--warn:#f5a623;--error:#ff5f5f;--tab-active:#00d4aa}
body{background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}
.container{width:100%;max-width:720px}
header{margin-bottom:2.5rem}
.badge{display:inline-block;background:rgba(0,212,170,.1);border:1px solid rgba(0,212,170,.3);color:var(--accent);font-family:'IBM Plex Mono',monospace;font-size:.7rem;padding:.25rem .75rem;border-radius:2px;letter-spacing:.1em;margin-bottom:1rem}
h1{font-size:2rem;font-weight:600;letter-spacing:-.02em;line-height:1.2}
h1 span{color:var(--accent)}
.subtitle{color:var(--muted);font-size:.9rem;margin-top:.5rem;font-weight:300}
.free-tag{display:inline-block;background:rgba(0,212,170,.08);border:1px solid rgba(0,212,170,.2);color:var(--accent);font-size:.7rem;padding:.2rem .6rem;border-radius:20px;margin-top:.75rem;font-family:'IBM Plex Mono',monospace}
/* Tabs */
.tabs{display:flex;gap:0;margin-bottom:0;border:1px solid var(--border);border-radius:8px 8px 0 0;overflow:hidden}
.tab-btn{flex:1;background:var(--surface);border:none;color:var(--muted);padding:.85rem 1rem;font-family:'IBM Plex Sans',sans-serif;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s;border-bottom:2px solid transparent}
.tab-btn:hover{color:var(--text)}
.tab-btn.active{color:var(--accent);background:var(--bg);border-bottom:2px solid var(--accent)}
.card{background:var(--surface);border:1px solid var(--border);border-top:none;border-radius:0 0 8px 8px;padding:2rem;margin-bottom:1.5rem}
.tab-panel{display:none}
.tab-panel.active{display:block}
label{display:block;font-size:.75rem;font-family:'IBM Plex Mono',monospace;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.5rem}
input[type=text]{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:.75rem 1rem;color:var(--text);font-family:'IBM Plex Mono',monospace;font-size:.9rem;outline:none;transition:border-color .2s;margin-bottom:1.25rem}
input[type=text]:focus{border-color:var(--accent)}
input[type=text].valid{border-color:var(--accent)}
input[type=text].invalid{border-color:var(--error)}
.cnpj-row{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem}
@media(max-width:540px){.cnpj-row{grid-template-columns:1fr}}
.cnpj-preview{background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:.6rem .9rem;font-size:.75rem;font-family:'IBM Plex Mono',monospace;color:var(--muted);min-height:2.4rem;margin-top:-.9rem;margin-bottom:1rem;line-height:1.5;display:none}
.cnpj-preview.show{display:block}
.cnpj-preview .co-name{color:var(--text);font-weight:600}
.upload-area{border:2px dashed var(--border);border-radius:6px;padding:2rem;text-align:center;cursor:pointer;transition:all .2s;position:relative;margin-bottom:.6rem}
.upload-area:hover,.upload-area.drag{border-color:var(--accent);background:rgba(0,212,170,.03)}
.upload-area input{position:absolute;inset:0;opacity:0;cursor:pointer}
.upload-icon{font-size:1.75rem;margin-bottom:.5rem}
.upload-text{color:var(--muted);font-size:.85rem}
.upload-text strong{color:var(--accent)}
.file-bar{display:none;align-items:center;gap:.75rem;background:rgba(0,212,170,.07);border:1px solid rgba(0,212,170,.25);border-radius:6px;padding:.6rem 1rem;margin-bottom:1rem}
.file-bar.show{display:flex}
.file-bar-name{flex:1;font-family:'IBM Plex Mono',monospace;font-size:.78rem;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.remove-file{flex-shrink:0;display:flex;align-items:center;justify-content:center;width:28px;height:28px;background:rgba(255,95,95,.15);border:1px solid rgba(255,95,95,.5);border-radius:4px;color:var(--error);cursor:pointer;font-size:.85rem;font-weight:700;transition:all .2s}
.remove-file:hover{background:rgba(255,95,95,.35);border-color:var(--error);transform:scale(1.05)}
.btn-calc{width:100%;background:var(--accent);color:#0f1117;border:none;border-radius:4px;padding:.9rem;font-family:'IBM Plex Sans',sans-serif;font-weight:600;font-size:.9rem;cursor:pointer;transition:opacity .2s;margin-top:.25rem}
.btn-calc:hover{opacity:.9}
.btn-calc:disabled{opacity:.4;cursor:not-allowed}
/* Result */
#result{display:none}
.result-card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:2rem;margin-bottom:1rem}
.result-header{display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem}
.dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.result-title{font-family:'IBM Plex Mono',monospace;font-size:.75rem;color:var(--accent);letter-spacing:.1em;text-transform:uppercase}
.metric{display:flex;justify-content:space-between;align-items:baseline;padding:.75rem 0;border-bottom:1px solid var(--border)}
.metric:last-child{border-bottom:none}
.metric-label{font-size:.78rem;color:var(--muted);font-family:'IBM Plex Mono',monospace}
.metric-value{font-weight:600}
.metric-value.big{font-size:1.5rem;color:var(--accent);font-family:'IBM Plex Mono',monospace}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem}
@media(max-width:520px){.two-col{grid-template-columns:1fr}}
.info-card{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:1rem}
.info-title{font-size:.68rem;font-family:'IBM Plex Mono',monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem}
.info-name{font-weight:600;font-size:.88rem;margin-bottom:.2rem;line-height:1.3}
.info-cnpj{font-family:'IBM Plex Mono',monospace;font-size:.73rem;color:var(--muted)}
.address-block{background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:.75rem 1rem;font-family:'IBM Plex Mono',monospace;font-size:.75rem;color:var(--muted);line-height:1.6;margin-top:.35rem;word-break:break-word}
.nivel-badge{display:inline-block;margin-top:.4rem;font-size:.68rem;font-family:'IBM Plex Mono',monospace;padding:.15rem .55rem;border-radius:20px}
.nivel-ok{background:rgba(0,212,170,.1);color:var(--accent);border:1px solid rgba(0,212,170,.25)}
.nivel-warn{background:rgba(245,166,35,.1);color:var(--warn);border:1px solid rgba(245,166,35,.25)}
.error-msg{background:rgba(255,95,95,.08);border:1px solid rgba(255,95,95,.3);border-radius:4px;padding:1rem;color:var(--error);font-size:.85rem;display:none;margin-top:1rem}
.spinner{display:none;text-align:center;padding:1rem 0;color:var(--muted);font-size:.85rem}
.spinner::before{content:'';display:inline-block;width:16px;height:16px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:.5rem}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="badge">NF-e TOOLS</div>
    <h1>Distância entre <span>emitente</span> e destinatário</h1>
    <p class="subtitle">Via XML da nota fiscal ou consulta direta por CNPJ.</p>
    <span class="free-tag">✓ 100% gratuito · sem API Key · BrasilAPI + OpenStreetMap + OSRM</span>
  </header>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab-btn active" onclick="setTab('xml')">📄 Upload XML</button>
    <button class="tab-btn" onclick="setTab('cnpj')">🏢 Consulta por CNPJ</button>
  </div>

  <div class="card">
    <!-- Painel XML -->
    <div class="tab-panel active" id="panel-xml">
      <label>Arquivo XML da NF-e</label>
      <div class="upload-area" id="uploadArea">
        <input type="file" id="xmlFile" accept=".xml">
        <div class="upload-icon">📄</div>
        <div class="upload-text"><strong>Clique para selecionar</strong> ou arraste aqui</div>
      </div>
      <div class="file-bar" id="fileBar">
        <span class="file-bar-name" id="fileNameText"></span>
        <button class="remove-file" onclick="removerArquivo()" title="Remover arquivo">✕</button>
      </div>
      <button class="btn-calc" onclick="calcularXml()">Calcular Distância</button>
    </div>

    <!-- Painel CNPJ -->
    <div class="tab-panel" id="panel-cnpj">
      <div class="cnpj-row">
        <div>
          <label>CNPJ do Emitente</label>
          <input type="text" id="cnpjEmit" placeholder="00.000.000/0001-00" maxlength="18" oninput="maskCnpj(this)" onblur="previewCnpj(this,'previewEmit')">
          <div class="cnpj-preview" id="previewEmit"></div>
        </div>
        <div>
          <label>CNPJ do Destinatário</label>
          <input type="text" id="cnpjDest" placeholder="00.000.000/0001-00" maxlength="18" oninput="maskCnpj(this)" onblur="previewCnpj(this,'previewDest')">
          <div class="cnpj-preview" id="previewDest"></div>
        </div>
      </div>
      <button class="btn-calc" onclick="calcularCnpj()">Calcular Distância</button>
    </div>

    <div class="spinner" id="spinner">Consultando e calculando rota...</div>
    <div class="error-msg" id="errorMsg"></div>
  </div>

  <!-- Resultado XML -->
  <div id="result-xml" style="display:none">
    <div class="result-card">
      <div class="result-header"><div class="dot"></div><div class="result-title">Resultado</div></div>
      <div class="metric">
        <span class="metric-label">DISTÂNCIA PELA ESTRADA</span>
        <span class="metric-value big" id="distancia-xml">—</span>
      </div>
      <div class="metric">
        <span class="metric-label">TEMPO ESTIMADO (carro)</span>
        <span class="metric-value" id="duracao-xml">—</span>
      </div>
      <div class="two-col">
        <div class="info-card">
          <div class="info-title">🏭 Emitente</div>
          <div class="info-name" id="emitNome-xml">—</div>
          <div class="info-cnpj" id="emitCnpj-xml">—</div>
        </div>
        <div class="info-card">
          <div class="info-title">📦 Destinatário</div>
          <div class="info-name" id="destNome-xml">—</div>
          <div class="info-cnpj" id="destCnpj-xml">—</div>
        </div>
      </div>
    </div>
    <div class="result-card">
      <div style="margin-bottom:1rem">
        <label>PONTO DE ORIGEM (resolvido)</label>
        <div class="address-block" id="endEmit-xml">—</div>
        <span class="nivel-badge" id="nivelEmit-xml"></span>
      </div>
      <div>
        <label>PONTO DE DESTINO (resolvido)</label>
        <div class="address-block" id="endDest-xml">—</div>
        <span class="nivel-badge" id="nivelDest-xml"></span>
      </div>
    </div>
  </div>

  <!-- Resultado CNPJ -->
  <div id="result-cnpj" style="display:none">
    <div class="result-card">
      <div class="result-header"><div class="dot"></div><div class="result-title">Resultado</div></div>
      <div class="metric">
        <span class="metric-label">DISTÂNCIA PELA ESTRADA</span>
        <span class="metric-value big" id="distancia-cnpj">—</span>
      </div>
      <div class="metric">
        <span class="metric-label">TEMPO ESTIMADO (carro)</span>
        <span class="metric-value" id="duracao-cnpj">—</span>
      </div>
      <div class="two-col">
        <div class="info-card">
          <div class="info-title">🏭 Emitente</div>
          <div class="info-name" id="emitNome-cnpj">—</div>
          <div class="info-cnpj" id="emitCnpj-cnpj">—</div>
        </div>
        <div class="info-card">
          <div class="info-title">📦 Destinatário</div>
          <div class="info-name" id="destNome-cnpj">—</div>
          <div class="info-cnpj" id="destCnpj-cnpj">—</div>
        </div>
      </div>
    </div>
    <div class="result-card">
      <div style="margin-bottom:1rem">
        <label>PONTO DE ORIGEM (resolvido)</label>
        <div class="address-block" id="endEmit-cnpj">—</div>
        <span class="nivel-badge" id="nivelEmit-cnpj"></span>
      </div>
      <div>
        <label>PONTO DE DESTINO (resolvido)</label>
        <div class="address-block" id="endDest-cnpj">—</div>
        <span class="nivel-badge" id="nivelDest-cnpj"></span>
      </div>
    </div>
  </div>
</div>

<script>
// Tabs — troca painel e mostra resultado da aba correspondente
function setTab(tab){
  document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active', (tab==='xml'&&i===0)||(tab==='cnpj'&&i===1)));
  document.getElementById('panel-xml').classList.toggle('active', tab==='xml');
  document.getElementById('panel-cnpj').classList.toggle('active', tab==='cnpj');
  document.getElementById('result-xml').style.display = (tab==='xml' && resultadoXml) ? 'block' : 'none';
  document.getElementById('result-cnpj').style.display = (tab==='cnpj' && resultadoCnpj) ? 'block' : 'none';
  document.getElementById('errorMsg').style.display='none';
}

// Upload XML
const uploadArea=document.getElementById('uploadArea'),fileInput=document.getElementById('xmlFile'),fileBar=document.getElementById('fileBar'),fileNameText=document.getElementById('fileNameText');
fileInput.addEventListener('change',()=>{
  if(fileInput.files[0]){
    fileNameText.textContent='✓  '+fileInput.files[0].name;
    fileBar.classList.add('show');
    uploadArea.style.opacity='.45';
    uploadArea.style.pointerEvents='none';
  }
});
['dragover','dragenter'].forEach(e=>uploadArea.addEventListener(e,ev=>{ev.preventDefault();uploadArea.classList.add('drag');}));
['dragleave','drop'].forEach(e=>uploadArea.addEventListener(e,()=>uploadArea.classList.remove('drag')));
uploadArea.addEventListener('drop',ev=>{ev.preventDefault();fileInput.files=ev.dataTransfer.files;fileInput.dispatchEvent(new Event('change'));});

function removerArquivo(){
  fileInput.value='';
  fileBar.classList.remove('show');
  fileNameText.textContent='';
  uploadArea.style.opacity='';
  uploadArea.style.pointerEvents='';
  document.getElementById('errorMsg').style.display='none';
}

async function calcularXml(){
  const file=fileInput.files[0];
  if(!file){showErr('Selecione um arquivo XML.');return;}
  const fd=new FormData(); fd.append('xml',file);
  await enviar('/calcular-xml', fd, null, 'xml');
}

// CNPJ mask
function maskCnpj(el){
  let v=el.value.replace(/\D/g,'').slice(0,14);
  if(v.length>12) v=v.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2}).*/,'$1.$2.$3/$4-$5');
  else if(v.length>8) v=v.replace(/^(\d{2})(\d{3})(\d{3})(\d{0,4}).*/,'$1.$2.$3/$4');
  else if(v.length>5) v=v.replace(/^(\d{2})(\d{3})(\d{0,3}).*/,'$1.$2.$3');
  else if(v.length>2) v=v.replace(/^(\d{2})(\d{0,3}).*/,'$1.$2');
  el.value=v;
  const digits=v.replace(/\D/g,'');
  el.classList.toggle('valid', digits.length===14);
  el.classList.toggle('invalid', digits.length>0 && digits.length<14);
}

async function previewCnpj(el, previewId){
  const digits=el.value.replace(/\D/g,'');
  const box=document.getElementById(previewId);
  if(digits.length!==14){box.classList.remove('show');return;}
  box.classList.add('show');
  box.textContent='Consultando...';
  try{
    const resp=await fetch('/consulta-cnpj',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cnpj:digits})});
    const data=await resp.json();
    if(data.erro){box.textContent='⚠ '+data.erro;return;}
    box.innerHTML=`<span class="co-name">${data.nome}</span><br>${data.municipio}/${data.uf}`;
  }catch(e){box.textContent='Erro ao consultar CNPJ.';}
}

async function calcularCnpj(){
  const emit=document.getElementById('cnpjEmit').value.replace(/\D/g,'');
  const dest=document.getElementById('cnpjDest').value.replace(/\D/g,'');
  if(emit.length!==14||dest.length!==14){showErr('Informe os dois CNPJs completos (14 dígitos).');return;}
  await enviar('/calcular-cnpj', JSON.stringify({cnpj_emit:emit, cnpj_dest:dest}), 'application/json', 'cnpj');
}

// Estado por aba
let resultadoXml=false, resultadoCnpj=false;

async function enviar(url, body, contentType, aba){
  const err=document.getElementById('errorMsg'),spin=document.getElementById('spinner');
  const btns=document.querySelectorAll('.btn-calc');
  err.style.display='none';
  btns.forEach(b=>b.disabled=true); spin.style.display='block';
  try{
    const opts={method:'POST',body};
    if(contentType) opts.headers={'Content-Type':contentType};
    const resp=await fetch(url,opts);
    const data=await resp.json();
    if(!resp.ok||data.erro){showErr(data.erro||'Erro desconhecido.');return;}
    renderResult(data, aba);
  }catch(e){showErr('Falha na comunicação com o servidor.');}
  finally{btns.forEach(b=>b.disabled=false); spin.style.display='none';}
}

const NIVEIS_EXATOS=['endereço completo','logradouro sem número','CEP','logradouro + município'];

function renderResult(data, aba){
  const id = 'result-'+aba;
  document.getElementById('distancia-'+aba).textContent=data.distancia_texto;
  document.getElementById('duracao-'+aba).textContent=data.duracao_texto;
  document.getElementById('emitNome-'+aba).textContent=data.emitente.nome;
  document.getElementById('emitCnpj-'+aba).textContent=data.emitente.cnpj;
  document.getElementById('destNome-'+aba).textContent=data.destinatario.nome;
  document.getElementById('destCnpj-'+aba).textContent=data.destinatario.cnpj;
  document.getElementById('endEmit-'+aba).textContent=data.origem_resolvida;
  document.getElementById('endDest-'+aba).textContent=data.destino_resolvido;
  setBadge('nivelEmit-'+aba, data.nivel_emit);
  setBadge('nivelDest-'+aba, data.nivel_dest);
  if(aba==='xml') resultadoXml=true; else resultadoCnpj=true;
  document.getElementById(id).style.display='block';
}

function setBadge(id,nivel){
  const el=document.getElementById(id);
  const ok=NIVEIS_EXATOS.includes(nivel);
  el.className='nivel-badge '+(ok?'nivel-ok':'nivel-warn');
  el.textContent=ok?'✓ Endereço localizado':'⚠ Aproximado via '+nivel;
}

function showErr(msg){const e=document.getElementById('errorMsg');e.textContent='⚠ '+msg;e.style.display='block';}
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_text(node, path):
    if node is None: return ''
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else ''


def parse_nfe(xml_bytes):
    root    = ET.fromstring(xml_bytes)
    inf_nfe = root.find('.//nfe:infNFe', NS)
    if inf_nfe is None:
        raise ValueError("Estrutura de NF-e não encontrada.")
    emit     = inf_nfe.find('nfe:emit', NS)
    end_emit = emit.find('nfe:enderEmit', NS) if emit is not None else None
    dest     = inf_nfe.find('nfe:dest', NS)
    end_dest = dest.find('nfe:enderDest', NS) if dest is not None else None

    def bloco(pai, end):
        return {
            'nome':        get_text(pai, 'nfe:xNome'),
            'cnpj':        get_text(pai, 'nfe:CNPJ') or get_text(pai, 'nfe:CPF'),
            'logradouro':  get_text(end, 'nfe:xLgr'),
            'numero':      get_text(end, 'nfe:nro'),
            'bairro':      get_text(end, 'nfe:xBairro'),
            'municipio':   get_text(end, 'nfe:xMun'),
            'uf':          get_text(end, 'nfe:UF'),
            'cep':         get_text(end, 'nfe:CEP'),
        }
    return {'emitente': bloco(emit, end_emit), 'destinatario': bloco(dest, end_dest)}


def consultar_cnpj(cnpj: str) -> dict:
    """Consulta dados do CNPJ via BrasilAPI (gratuito, sem limite, sem API key)."""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    if len(cnpj_limpo) != 14:
        raise ValueError(f"CNPJ inválido: {cnpj}")

    url  = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    resp = requests.get(url, timeout=15, headers={'User-Agent': 'nfe-distancia-app/1.0'})

    if resp.status_code == 404:
        raise ValueError(f"CNPJ não encontrado: {cnpj_limpo}")
    if resp.status_code == 400:
        raise ValueError(f"CNPJ inválido: {cnpj_limpo}")
    resp.raise_for_status()

    data = resp.json()

    logradouro = data.get('logradouro', '')
    numero     = data.get('numero', '')
    bairro     = data.get('bairro', '')
    municipio  = data.get('municipio', '')
    uf         = data.get('uf', '')
    cep        = re.sub(r'\D', '', data.get('cep', ''))
    nome       = data.get('razao_social', '') or data.get('nome_fantasia', '')

    return {
        'nome':       nome,
        'cnpj':       cnpj_limpo,
        'logradouro': logradouro,
        'numero':     numero,
        'bairro':     bairro,
        'municipio':  municipio,
        'uf':         uf,
        'cep':        cep,
    }


def geocodificar(dados: dict):
    headers = {'User-Agent': 'nfe-distancia-app/1.0'}
    rua = dados.get('logradouro', '').strip()
    num = dados.get('numero', '').strip()
    mun = dados.get('municipio', '').strip()
    uf  = dados.get('uf', '').strip()
    cep = re.sub(r'\D', '', dados.get('cep', '')).zfill(8)
    cep_fmt = f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else cep

    tentativas = []

    # 1. Endereço completo (rua + número + município + UF + CEP)
    if rua and num and mun and uf and cep:
        tentativas.append((f"{rua}, {num}, {mun}, {uf}, {cep_fmt}, Brasil", "endereço completo"))

    # 2. Rua + número + município + UF (sem CEP)
    if rua and num and mun and uf:
        tentativas.append((f"{rua}, {num}, {mun}, {uf}, Brasil", "endereço completo"))

    # 3. Rua + município + UF (sem número)
    if rua and mun and uf:
        tentativas.append((f"{rua}, {mun}, {uf}, Brasil", "logradouro sem número"))

    # 4. CEP + município + UF (ancora o CEP na cidade certa)
    if cep and mun and uf:
        tentativas.append((f"{cep_fmt}, {mun}, {uf}, Brasil", "CEP"))

    # 5. Marco zero — praça central
    if mun and uf:
        tentativas.append((f"Praça Central, {mun}, {uf}, Brasil", "marco zero (praça central)"))

    # 6. Marco zero — prefeitura
    if mun and uf:
        tentativas.append((f"Prefeitura Municipal de {mun}, {uf}, Brasil", "marco zero (prefeitura)"))

    # 7. Marco zero — câmara municipal
    if mun and uf:
        tentativas.append((f"Câmara Municipal de {mun}, {uf}, Brasil", "marco zero (câmara municipal)"))

    # 8. Só município + UF (último recurso)
    if mun and uf:
        tentativas.append((f"{mun}, {uf}, Brasil", "município"))

    for i, (query, nivel) in enumerate(tentativas):
        if i > 0:
            time.sleep(1)
        try:
            resp = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'br'},
                headers=headers, timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
            if results:
                # Valida que o resultado pertence ao município/UF esperado
                display = results[0]['display_name'].lower()
                mun_lower = mun.lower()
                uf_lower  = uf.lower()
                # Aceita se município ou UF aparecer no display_name, ou se for tentativa de último recurso
                if mun_lower in display or uf_lower in display or nivel == "município":
                    return float(results[0]['lat']), float(results[0]['lon']), results[0]['display_name'], nivel
        except Exception:
            continue

    raise ValueError(f"Não foi possível localizar '{mun}/{uf}' após todas as tentativas.")


def calcular_rota(lat1, lon1, lat2, lon2):
    url  = f'http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}'
    resp = requests.get(url, params={'overview': 'false'}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if data.get('code') != 'Ok':
        raise ValueError(f"Erro OSRM: {data.get('code')}")
    rota   = data['routes'][0]
    dist_m = rota['distance']
    dur_s  = rota['duration']
    dist_txt = f"{round(dist_m/1000)} km" if dist_m >= 1000 else f"{dist_m:.0f} m"
    h, m = int(dur_s // 3600), int((dur_s % 3600) // 60)
    dur_txt = f"{h}h {m}min" if h > 0 else f"{m} min"
    return {'distancia_texto': dist_txt, 'distancia_metros': dist_m, 'duracao_texto': dur_txt}


def montar_resposta(emit, dest):
    """Geocodifica, calcula rota e monta o JSON de resposta."""
    lat1, lon1, end1, nivel1 = geocodificar(emit)
    time.sleep(1)
    lat2, lon2, end2, nivel2 = geocodificar(dest)
    resultado = calcular_rota(lat1, lon1, lat2, lon2)
    return {
        **resultado,
        'origem_resolvida':  end1,
        'destino_resolvido': end2,
        'nivel_emit':        nivel1,
        'nivel_dest':        nivel2,
        'emitente':          {'nome': emit['nome'], 'cnpj': emit['cnpj']},
        'destinatario':      {'nome': dest['nome'], 'cnpj': dest['cnpj']},
    }

# ---------------------------------------------------------------------------
# Rotas Flask
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/calcular-xml', methods=['POST'])
def calcular_xml():
    try:
        xml_file = request.files.get('xml')
        if not xml_file:
            return jsonify({'erro': 'Arquivo XML não enviado.'}), 400
        dados = parse_nfe(xml_file.read())
        return jsonify(montar_resposta(dados['emitente'], dados['destinatario']))
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


@app.route('/calcular-cnpj', methods=['POST'])
def calcular_cnpj():
    try:
        body       = request.get_json(force=True)
        cnpj_emit  = body.get('cnpj_emit', '')
        cnpj_dest  = body.get('cnpj_dest', '')
        if not cnpj_emit or not cnpj_dest:
            return jsonify({'erro': 'Informe os dois CNPJs.'}), 400

        emit = consultar_cnpj(cnpj_emit)
        time.sleep(1)   # Respeita limite da ReceitaWS (1 req/s)
        dest = consultar_cnpj(cnpj_dest)

        return jsonify(montar_resposta(emit, dest))
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


@app.route('/consulta-cnpj', methods=['POST'])
def consulta_cnpj_preview():
    """Preview rápido do CNPJ para mostrar nome/cidade enquanto digita."""
    try:
        body = request.get_json(force=True)
        cnpj = body.get('cnpj', '')
        data = consultar_cnpj(cnpj)
        return jsonify({'nome': data['nome'], 'municipio': data['municipio'], 'uf': data['uf']})
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Servidor iniciado em http://localhost:5000")
    app.run(debug=True, port=5000)
