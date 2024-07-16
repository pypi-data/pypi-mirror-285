from pathlib import Path
import importlib

def load_questions(pattern='_qmnli.py'):
    base_path = Path(__file__).parent.parent
    questions = []
    for questionnaire_path in list(base_path.glob(f'**/*{pattern}')):
        questionnaire_path = questionnaire_path.relative_to(base_path)
        name = questionnaire_path.name.replace(".py", "")
        file = questionnaire_path
        module_path = str(questionnaire_path.parent).replace('/', '.') + f'.{name}'
        module = importlib.import_module(module_path)
        if hasattr(module, name):
            print('load:', name)
            questions += getattr(module, name)
            
    return questions