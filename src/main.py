from typing import List, Dict, Any
from typing_extensions import LiteralString
import os
from dotenv import load_dotenv
import google.generativeai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext

BASE_INIT_PROMPT = "Answer to the following prompt with only the source code in Python: "
BASE_FEEDBACK = "Adjust the previous code following this instruction: "

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
gemini = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config=genai.GenerationConfig(temperature=0.5),
)
chat = gemini.start_chat(history=[])
history: List[str] = []

def submit_prompt() -> None:
    init_prompt, feedback = init_prompt_input.get(), feedback_input.get()
    _clear_inputs()

    if init_prompt:
        if len(history) > 0:
            _clear_history()

        response = _send_init_prompt(init_prompt)
        _add_to_history(init_prompt, response)
        code_display.config(state=tk.NORMAL)
        code_display.delete(1.0, tk.END)
        code_display.insert(tk.END, response)
        code_display.config(state=tk.DISABLED)

    elif feedback and len(history) > 0:
        improved_response = _send_feedback(feedback)
        _add_to_history(feedback, improved_response)
        code_display.config(state=tk.NORMAL)
        code_display.delete(1.0, tk.END)
        code_display.insert(tk.END, improved_response)
        code_display.config(state=tk.DISABLED)

    _update_history_display()
    _update_dropdown()

def _clear_inputs() -> None:
    init_prompt_input.delete(0, tk.END)
    feedback_input.delete(0, tk.END)

def _clear_history() -> None:
    chat.history.clear()
    history.clear()
    version_dropdown['values'] = []
    history_display.config(state=tk.NORMAL)
    history_display.delete(1.0, tk.END)
    history_display.config(state=tk.DISABLED)

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
    history_display.config(state=tk.NORMAL)
    history_display.delete(1.0, tk.END)
    history_display.insert(tk.END, "\n\n\n".join(history))
    history_display.config(state=tk.DISABLED)

def _update_dropdown() -> None:
    qt_versions = len(history)
    version_dropdown['values'] = [f"Versão {index}" for index in range(qt_versions, 1-1, -1)]

def on_version_select(event) -> None:
    chosen_version = int(version_dropdown.get().split(" ")[-1])
    qt_versions = len(history)

    while qt_versions > chosen_version:
        for _ in range(2):
            chat.history.pop()
        history.pop()
        qt_versions -= 1

    _update_dropdown()
    code_display.config(state=tk.NORMAL)
    code_display.delete(1.0, tk.END)
    code_display.insert(tk.END, _remove_md(chat.history[-1].parts[0].text))
    code_display.config(state=tk.DISABLED)
    _update_history_display()

root = tk.Tk()
root.title("DevPal")

init_prompt_input = tk.Entry(root, width=80)
init_prompt_input.grid(row=0, column=0, padx=10, pady=10)

feedback_input = tk.Entry(root, width=80)
feedback_input.grid(row=0, column=1, padx=10, pady=10)

submit_button = tk.Button(root, text="Enviar", command=submit_prompt)
submit_button.grid(row=1, column=0, columnspan=2, pady=10)

version_dropdown = ttk.Combobox(root, state="readonly")
version_dropdown.grid(row=2, column=0, columnspan=2, pady=10)
version_dropdown.bind("<<ComboboxSelected>>", on_version_select)

code_display = scrolledtext.ScrolledText(root, width=80, height=20, state=tk.DISABLED)
code_display.grid(row=3, column=0, padx=10, pady=10)

history_display = scrolledtext.ScrolledText(root, width=40, height=20, state=tk.DISABLED)
history_display.grid(row=3, column=1, padx=10, pady=10)

if __name__=="__main__":
    root.mainloop()
