from pathlib import Path

path = Path("app/services/internship_service.py")
code = path.read_text()

# Add safe embedding refresh helper

helper = '''

# ==========================================
# AUTOMATIC INTERNSHIP EMBEDDING REFRESH
# ==========================================

def refresh_internship_embedding_safely(internship_id):
    """Refresh internship embedding without undoing database changes."""

    try:
        from app.services.embedding_db_service import (
            generate_internship_embedding
        )

        generate_internship_embedding(internship_id)

        print(f"Internship embedding refreshed: {internship_id}")

    except Exception as error:
        print(
            f"Internship embedding refresh failed "
            f"for {internship_id}: {error}"
        )


'''

marker = "# ==========================================\n# CREATE INTERNSHIP"

if "def refresh_internship_embedding_safely" not in code:
    if marker not in code:
        raise ValueError("CREATE INTERNSHIP section not found.")

    code = code.replace(marker, helper + marker, 1)


# Functions requiring automatic embedding refresh

functions = [
    ("def create_internship", "return result[0]", False),
    ("def update_internship", "return result is not None", True),
    ("def add_internship_skill", "return result is not None", True),
]

for function_name, return_line, check_result in functions:

    start = code.index(function_name)
    end = code.find("\ndef ", start + 1)

    if end == -1:
        end = len(code)

    section = code[start:end]

    if "refresh_internship_embedding_safely(internship_id)" in section:
        continue

    if return_line not in section:
        raise ValueError(f"Return statement not found: {function_name}")

    if check_result:
        insertion = (
            "if result:\n"
            "                refresh_internship_embedding_safely(internship_id)\n\n"
            "            "
        )
    else:
        insertion = (
            "refresh_internship_embedding_safely(result[0])\n\n            "
        )

    section = section.replace(return_line, insertion + return_line, 1)

    code = code[:start] + section + code[end:]


path.write_text(code)

print("Internship embedding integration completed.")
