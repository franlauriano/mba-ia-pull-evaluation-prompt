"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
V2_FILE = PROMPTS_DIR / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_prompt_v2_data():
    """Carrega e retorna os dados do prompt v2."""
    if not V2_FILE.exists():
        pytest.skip(f"Arquivo {V2_FILE} não encontrado")
    data = load_prompts(str(V2_FILE))
    if not data or PROMPT_KEY not in data:
        pytest.skip(f"Chave '{PROMPT_KEY}' não encontrada no YAML")
    return data[PROMPT_KEY]


def get_full_prompt_text(prompt_data: dict) -> str:
    """Retorna todo o texto do prompt (system + user) para buscas."""
    parts = [
        prompt_data.get("system_prompt", ""),
        prompt_data.get("user_prompt", ""),
    ]
    return " ".join(str(p) for p in parts if p)


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = get_prompt_v2_data()
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        system = prompt_data["system_prompt"]
        assert system is not None, "system_prompt não pode ser None"
        assert str(system).strip(), "system_prompt não pode estar vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = get_prompt_v2_data()
        text = get_full_prompt_text(prompt_data).lower()
        assert "você é" in text or "product manager" in text or "persona" in text or "analista" in text, (
            "O prompt deve definir uma persona (ex: 'Você é um Product Manager')"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = get_prompt_v2_data()
        text = get_full_prompt_text(prompt_data)
        format_indicators = [
            "como",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "dado",
            "quando",
            "então",
            "user story",
            "markdown",
        ]
        text_lower = text.lower()
        found = any(ind in text_lower for ind in format_indicators)
        assert found, "O prompt deve mencionar formato User Story ou Markdown (Como... Eu quero... Para que... ou Critérios Dado/Quando/Então)"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = get_prompt_v2_data()
        text = get_full_prompt_text(prompt_data).lower()
        has_example_label = "exemplo" in text or "few-shot" in text or "entrada" in text
        has_input_output = ("bug" in text and "user story" in text) or ("entrada" in text and "saída" in text)
        assert has_example_label or has_input_output, (
            "O prompt deve conter exemplos de entrada/saída (técnica Few-shot)"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = get_prompt_v2_data()
        text = get_full_prompt_text(prompt_data)
        assert "[TODO]" not in text and "[todo]" not in text, (
            "O prompt não deve conter [TODO] não resolvido"
        )

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = get_prompt_v2_data()
        techniques = prompt_data.get("techniques_applied")
        assert techniques is not None, "Campo 'techniques_applied' não encontrado no YAML"
        assert isinstance(techniques, (list, tuple)), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
