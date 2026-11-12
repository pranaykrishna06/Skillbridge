from pathlib import Path

path = Path("app/services/student_service.py")
code = path.read_text()

helper = '''

# ==========================================
# AUTOMATIC EMBEDDING REFRESH
# ==========================================

def refresh_student_embedding_safely(student_id):
    """Refresh embedding without undoing database changes."""

    try:
        from app.services.embedding_db_service import (
            generate_student_embedding
        )

        generate_student_embedding(student_id)
        print(f"Student embedding refreshed: {student_id}")

    except Exception as error:
        print(f"Embedding refresh failed for {student_id}: {error}")


'''

marker = "# ==========================================\n# STUDENT PROFILE"

if "def refresh_student_embedding_safely" not in code:
    code = code.replace(marker, helper + marker, 1)

functions = [
    ("def create_student_profile", "return result", False),
    ("def update_student_profile", "return result is not None", True),
    ("def add_student_skill", "return result is not None", True),
    ("def delete_student_skill", "return result is not None", True),
    ("def add_student_project", "return result[0]", True),
    ("def delete_student_project", "return result is not None", True),
]

for function_name, return_line, check_result in functions:

    start = code.index(function_name)
    end = code.find("\ndef ", start + 1)

    if end == -1:
        end = len(code)

    section = code[start:end]

    if "refresh_student_embedding_safely(student_id)" in section:
        continue

    if return_line not in section:
        raise ValueError(f"Return statement not found: {function_name}")

    if check_result:
        insertion = (
            "if result:\n"
            "                refresh_student_embedding_safely(student_id)\n\n"
            "            "
        )
    else:
        insertion = (
            "refresh_student_embedding_safely(student_id)\n\n            "
        )

    section = section.replace(return_line, insertion + return_line, 1)

    code = code[:start] + section + code[end:]

path.write_text(code)

print("All six student operations patched successfully.")
