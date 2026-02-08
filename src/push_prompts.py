"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê o prompt do arquivo YAML indicado por PROMPT_KEY_PUSH_TO_LANGSMITH_HUB (ex.: bug_to_user_story_v2 → prompts/bug_to_user_story_v2.yml)
2. Valida a estrutura do prompt
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

Requer no .env: LANGSMITH_API_KEY, USERNAME_LANGSMITH_HUB, PROMPT_KEY_PUSH_TO_LANGSMITH_HUB.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def _get_prompt_config():
    """Lê arquivo e chave do prompt a partir da env PROMPT_KEY_PUSH_TO_LANGSMITH_HUB."""
    key = (os.getenv("PROMPT_KEY_PUSH_TO_LANGSMITH_HUB") or "").strip()
    if not key:
        return None, None
    return f"prompts/{key}.yml", key


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)
    if not is_valid:
        return (False, errors)
    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio ou ausente")
        return (False, errors)
    return (True, [])


def _build_prompt_template(prompt_data: dict) -> ChatPromptTemplate:
    """Monta ChatPromptTemplate a partir do dict do YAML."""
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo do repositório (ex: username/bug_to_user_story_v2)
        prompt_data: Dados do prompt (description, system_prompt, user_prompt, etc.)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt_template = _build_prompt_template(prompt_data)
        description = prompt_data.get("description", "Prompt otimizado Bug to User Story")
        tags = list(prompt_data.get("tags", []))
        techniques = prompt_data.get("techniques_applied", [])
        if techniques:
            tags = list(tags) + [f"technique:{t}" for t in techniques]

        hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags,
        )
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    PROMPT_FILE, PROMPT_KEY = _get_prompt_config()
    if not PROMPT_KEY:
        print("❌ PROMPT_KEY_PUSH_TO_LANGSMITH_HUB não configurado no .env")
        print("   Ex.: PROMPT_KEY_PUSH_TO_LANGSMITH_HUB=bug_to_user_story_v2")
        return 1

    base_dir = Path(__file__).resolve().parent.parent
    prompt_path = base_dir / PROMPT_FILE

    if not prompt_path.exists():
        print(f"❌ Arquivo não encontrado: {PROMPT_FILE}")
        return 1

    data = load_yaml(str(prompt_path))
    if not data:
        return 1

    prompt_data = data.get(PROMPT_KEY)
    if not prompt_data:
        print(f"❌ Chave '{PROMPT_KEY}' não encontrada no YAML.")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Validação falhou:")
        for err in errors:
            print(f"   - {err}")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return 1

    repo_full_name = f"{username}/{PROMPT_KEY}"
    print(f"Enviando prompt para: {repo_full_name}")

    if push_prompt_to_langsmith(repo_full_name, prompt_data):
        print(f"   ✓ Push concluído. Prompt público em: https://smith.langchain.com/hub/{repo_full_name}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
