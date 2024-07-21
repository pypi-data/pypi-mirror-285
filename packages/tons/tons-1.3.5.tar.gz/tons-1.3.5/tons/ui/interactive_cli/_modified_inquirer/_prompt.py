from ._render import ModifiedConsoleRender
from ._theme import ModifiedTheme


class ModifiedPrompt:
    @staticmethod
    def _prompt(questions):
        render = ModifiedConsoleRender(theme=ModifiedTheme())
        answers = dict()
        for idx, question in enumerate(questions):
            answers[question.name] = render.render(question, answers)
        return answers
