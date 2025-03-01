from typing import List, Dict, Any
from typing_extensions import LiteralString
import os
from dotenv import load_dotenv
import google.generativeai as genai
from ipywidgets import Text, Dropdown, Textarea, Layout, Button, VBox, HBox
from IPython.display import display

BASE_INIT_PROMPT = "Responda o seguinte prompt com apenas um código fonte em Python: "
BASE_FEEDBACK = "Ajuste o código anterior conforme à seguinte instrução: "

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
gemini = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config=genai.GenerationConfig(temperature=0.5),
)
chat = gemini.start_chat(history=[])
history: List[str] = []

box_layout = Layout(
    display='flex',
    flex_flow='column',
    align_items='center',
    background_color='#2E2E2E',
    padding='20px',
    width='1300px',
    height='800px'
)

init_prompt_input = Text(
    value='',
    placeholder='ex: Gerar 2 números aleatórios',
    description='Descrição do código:',
    disabled=False,
    style={'description_width': 'initial'},
    layout=Layout(width='80%', padding='15px', border='solid 2px #444', margin='10px', justify_content='center')
)

feedback_input = Text(
    value='',
    placeholder='ex: Melhore a eficiência do código',
    description='Feedback:',
    disabled=False,
    style={'description_width': 'initial'},
    layout=Layout(width='80%', padding='15px', border='solid 2px #444', margin='10px', justify_content='center')
)

history_display = Textarea(
    value='',
    placeholder='Histórico de Códigos',
    disabled=True,
    layout=Layout(width='40%', height='600px', margin='10px')
)

code_display = Textarea(
    value='',
    placeholder='Versao atual do código',
    disabled=True,
    layout=Layout(width='60%', height='600px', margin='10px')
)

version_dropdown = Dropdown(
    options=[],
    disabled=False,
    layout=Layout(width='40%', height='40px', margin='10px')
)

button = Button(
    description='Enviar',
    disabled=False,
    button_style='primary',
    tooltip='Clique para enviar',
    icon='check',
    layout=Layout(width='60%', height='40px', margin='10px', justify_content='center')
)

def submit_prompt(clicked_button: Button) -> None:
    init_prompt, feedback = init_prompt_input.value, feedback_input.value
    _clear_inputs()

    if init_prompt:
        if len(history) > 0:
            _clear_history()

        response = _send_init_prompt(init_prompt)
        _add_to_history(init_prompt, response)
        code_display.value = response

    elif feedback and len(history) > 0:
        improved_response = _send_feedback(feedback)
        _add_to_history(feedback, improved_response)
        code_display.value = improved_response

    _update_history_display()
    _update_dropdown()

def _clear_inputs() -> None:
    init_prompt_input.value = ""
    feedback_input.value = ""

def _clear_history() -> None:
    chat.history.clear()
    history.clear()
    version_dropdown.options = tuple()
    history_display.value = ""

def _send_init_prompt(user_input: str) -> LiteralString:
    prompt = BASE_INIT_PROMPT + user_input
    response = chat.send_message(prompt)
    content = _remove_md(response.text)
    return content

def _add_to_history(prompt: str, response: LiteralString) -> None:
    history.append(f"[{len(history) + 1}] {prompt}\n\nResposta:\n{response}")

def _send_feedback(user_input: str) -> LiteralString:
    prompt = BASE_FEEDBACK + user_input
    response = chat.send_message(prompt)
    content = _remove_md(response.text)
    return content

def _remove_md(text: LiteralString) -> LiteralString:
    return text.split("```python\n")[-1].split("```")[0]

def _update_history_display() -> None:
    history_display.value = "\n\n\n".join(history)

def _update_dropdown() -> None:
    qt_versions = len(history)
    version_dropdown.options = tuple(f"Versão {index}" for index in range(qt_versions, 1-1, -1))

def on_version_select(change: Dict[str, Any]) -> None:
    if not change['new']:
        return

    chosen_version = int(change['new'].split(" ")[-1])
    qt_versions = len(history)

    while qt_versions > chosen_version:
        for _ in range(2):
            chat.history.pop()
        history.pop()
        qt_versions-=1
    
    _update_dropdown()
    code_display.value = _remove_md(chat.history[-1].parts[0].text)
    _update_history_display()

version_dropdown.observe(on_version_select, names='value')
button.on_click(submit_prompt)

layout = VBox([
    HBox([init_prompt_input, feedback_input]),
    HBox([button,version_dropdown]),
    HBox([code_display, history_display])
])

display(layout)
