from app.schemas import FullProfile

def escape_latex(text: str) -> str:
    if not text:
        return ""
    replacements = {
        '\\': '\\textbackslash{}',
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def generate_latex_content(profile: FullProfile) -> str:
    researcher = profile.researcher
    tex_content = f"""\\documentclass[11pt]{{article}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\begin{{document}}
\\begin{{center}}
{{\\huge \\textbf{{{escape_latex(researcher.full_name or '')}}}}} \\\\
{escape_latex(researcher.job_title or '')} \\\\
\\texttt{{{escape_latex(researcher.contact_email or '')}}}
\\end{{center}}
\\section*{{Profile}}
{escape_latex(researcher.profile_desc or '')}
\\section*{{Research Interests}}
{escape_latex(researcher.research_interests or '')}
\\section*{{Experience}}
"""
    for exp in profile.experiences:
        tex_content += f"\\subsection*{{{escape_latex(exp.title)} at {escape_latex(exp.company)}}} ({escape_latex(exp.period)})\n{escape_latex(exp.description)}\n\n"
    tex_content += "\\section*{Education}\n"
    for edu in profile.educations:
        tex_content += f"\\subsection*{{{escape_latex(edu.degree)}, {escape_latex(edu.institution)}}} {escape_latex(edu.details)}\n\n"
    tex_content += "\\section*{Publications}\n\\begin{itemize}\n"
    for pub in profile.publications:
        tex_content += f"\\item {escape_latex(pub.title)}. {escape_latex(pub.authors or '')} {escape_latex(pub.journal or '')} ({pub.year or ''}).\n"
    tex_content += "\\end{itemize}\n\\end{document}"
    
    return tex_content
