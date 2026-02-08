"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env (USERNAME_LANGSMITH_HUB, PROMPT_KEY_PULL_FROM_LANGSMITH_HUB)
2. Faz pull do prompt do Hub
3. Salva localmente em prompts/{PROMPT_KEY_PULL_FROM_LANGSMITH_HUB}.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_HUB_ID = f"{os.getenv('USERNAME_LANGSMITH_HUB')}/{os.getenv('PROMPT_KEY_PULL_FROM_LANGSMITH_HUB')}"
OUTPUT_PATH = f"prompts/{os.getenv('PROMPT_KEY_PULL_FROM_LANGSMITH_HUB')}.yml"


def _template_to_serializable(prompt_template: ChatPromptTemplate) -> dict:
    """
    Converte um ChatPromptTemplate em estrutura serializável (dict) para YAML.
    Extrai system_prompt e user_prompt dos messages.
    """
    system_prompt = ""
    user_prompt = ""

    for message in prompt_template.messages:
        template_str = ""
        if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
            template_str = message.prompt.template
        elif hasattr(message, "template"):
            template_str = message.template

        type_name = type(message).__name__.lower()
        if "system" in type_name:
            system_prompt = template_str
        elif "human" in type_name:
            user_prompt = template_str

    return {
        "system_prompt": system_prompt or "",
        "user_prompt": user_prompt or "{bug_report}",
    }


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt do LangSmith Hub e salva em prompts/{PROMPT_KEY_PULL_FROM_LANGSMITH_HUB}.yml.

    Returns:
        True se sucesso, False caso contrário.
    """
    print(f"Puxando prompt do Hub: {PROMPT_HUB_ID}")
    try:
        prompt_template = hub.pull(PROMPT_HUB_ID)
        if not isinstance(prompt_template, ChatPromptTemplate):
            print("❌ O objeto retornado não é um ChatPromptTemplate.")
            return False
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ Erro ao fazer pull: {e}")
        if "not found" in error_msg or "404" in error_msg:
            print("   Verifique se o prompt existe no LangSmith Hub e se LANGSMITH_API_KEY está correta.")
        return False

    data = _template_to_serializable(prompt_template)

    # Estrutura compatível com o formato esperado (nome do prompt como chave)
    output_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories (pull do LangSmith Hub)",
            "system_prompt": data["system_prompt"],
            "user_prompt": data["user_prompt"],
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    base_dir = Path(__file__).resolve().parent.parent
    output_file = base_dir / OUTPUT_PATH
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if not save_yaml(output_data, str(output_file)):
        return False

    print(f"   ✓ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    if pull_prompts_from_langsmith():
        print("\n✓ Pull concluído com sucesso.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
