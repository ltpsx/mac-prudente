#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de atualização automática PRUDENTE para N8N
Executa: Exportação -> Geração App -> Deploy -> Git Push
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Configura encoding UTF-8 para o console Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_DIR = Path(__file__).parent.parent

def log(mensagem, nivel="INFO"):
    """Log formatado com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{nivel}] {mensagem}")

def executar_comando(comando, descricao, cwd=None, critical=True):
    """Executa um comando e retorna True se sucesso"""
    log(f"Iniciando: {descricao}", "INFO")

    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(cwd or BASE_DIR),
            timeout=300  # 5 minutos de timeout
        )

        if resultado.stdout:
            for linha in resultado.stdout.strip().split('\n'):
                if linha.strip():
                    log(linha, "OUTPUT")

        log(f"Concluído: {descricao}", "SUCCESS")
        return True

    except subprocess.TimeoutExpired:
        log(f"Timeout: {descricao}", "ERROR")
        return not critical

    except subprocess.CalledProcessError as e:
        log(f"Falhou: {descricao}", "ERROR")
        log(f"Código de saída: {e.returncode}", "ERROR")
        if e.stderr:
            log(f"Erro: {e.stderr}", "ERROR")

        # Git commit sem mudanças não é erro crítico
        if "git commit" in comando and "nothing to commit" in str(e.stderr):
            log("Sem mudanças para commit - OK", "INFO")
            return True

        return not critical

    except Exception as e:
        log(f"Erro inesperado: {descricao} - {str(e)}", "ERROR")
        return not critical

def main():
    inicio = datetime.now()
    log("="*60, "INFO")
    log("ATUALIZAÇÃO AUTOMÁTICA PRUDENTE - N8N", "INFO")
    log("="*60, "INFO")

    # Estatísticas
    stats = {
        "inicio": inicio.isoformat(),
        "etapas_sucesso": 0,
        "etapas_erro": 0,
        "etapas": []
    }

    # Lista de tarefas
    tarefas = [
        {
            "comando": "python exportar_tabela_prudente_app.py",
            "descricao": "Exportar CSV da Tabela Prudente (TAB00007 ALMOX 5)",
            "cwd": BASE_DIR,
            "critical": True
        },
        {
            "comando": "python gerar_app.py",
            "descricao": "Gerar App de Pedidos Prudente",
            "cwd": BASE_DIR / "App Pedidos Prudente",
            "critical": True
        },
        {
            "comando": "python preparar_deploy.py",
            "descricao": "Preparar Deploy",
            "cwd": BASE_DIR / "prudente-deploy",
            "critical": True
        },
        {
            "comando": f'set GIT_TERMINAL_PROMPT=0&& set GCM_INTERACTIVE=never&& git add docs/ .gitignore && git diff --quiet && git diff --staged --quiet || (git commit --no-verify -m "Atualização automática N8N - {datetime.now().strftime("%d/%m/%Y %H:%M")}" && (git push || timeout /t 10 && git push || timeout /t 30 && git push))',
            "descricao": "Git Commit e Push (com retry)",
            "cwd": BASE_DIR / "prudente-deploy",
            "critical": False  # Sem mudanças não é erro
        }
    ]

    # Executa todas as tarefas
    for i, tarefa in enumerate(tarefas, 1):
        etapa = f"{i}/{len(tarefas)}"
        descricao_completa = f"[{etapa}] {tarefa['descricao']}"

        sucesso = executar_comando(
            tarefa["comando"],
            descricao_completa,
            tarefa.get("cwd"),
            tarefa.get("critical", True)
        )

        stats["etapas"].append({
            "nome": tarefa["descricao"],
            "sucesso": sucesso,
            "critical": tarefa.get("critical", True)
        })

        if sucesso:
            stats["etapas_sucesso"] += 1
        else:
            stats["etapas_erro"] += 1
            if tarefa.get("critical", True):
                log(f"Etapa crítica falhou: {tarefa['descricao']}", "ERROR")
                log("Interrompendo execução", "ERROR")
                break

    # Resumo final
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    stats["fim"] = fim.isoformat()
    stats["duracao_segundos"] = duracao

    log("="*60, "INFO")
    log("RESUMO DA EXECUÇÃO", "INFO")
    log("="*60, "INFO")
    log(f"Etapas concluídas: {stats['etapas_sucesso']}/{len(tarefas)}", "INFO")
    log(f"Etapas com erro: {stats['etapas_erro']}", "INFO")
    log(f"Duração: {duracao:.1f} segundos", "INFO")

    if stats["etapas_erro"] == 0:
        log("EXECUÇÃO COMPLETA - SUCESSO TOTAL!", "SUCCESS")
        log("Deploy será publicado em ~1 minuto", "INFO")
        exit_code = 0
    else:
        log(f"EXECUÇÃO COM {stats['etapas_erro']} ERRO(S)", "WARNING")
        exit_code = 1

    # Salva log JSON para n8n (opcional)
    log_file = BASE_DIR / "prudente-deploy" / "ultimo_log.json"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        log(f"Log salvo em: {log_file}", "INFO")
    except Exception as e:
        log(f"Erro ao salvar log: {e}", "WARNING")

    log("="*60, "INFO")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
