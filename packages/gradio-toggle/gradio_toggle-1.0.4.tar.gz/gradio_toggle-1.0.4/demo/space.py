
import gradio as gr
from app import demo as app
import os

_docs = {'Toggle': {'description': 'A toggle component that represents a boolean value, allowing users to switch between True and False states. Can function both as an input, to capture user interaction, and as an output, to display a boolean state.\n', 'members': {'__init__': {'value': {'type': 'bool | Callable', 'default': 'False', 'description': 'Initial state of the toggle. If callable, it sets the initial state dynamically when the app loads.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'Text label displayed adjacent to the toggle. If None and used within a `gr.Interface`, it defaults to the parameter name.'}, 'info': {'type': 'str | None', 'default': 'None', 'description': 'Text displayed below the toggle for additional guidance or information.'}, 'color': {'type': 'str | Callable | None', 'default': 'None', 'description': 'Optional color setting for the toggle, supporting CSS color values (e.g., names, hex codes).'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'If value is callable, specifies how frequently (in seconds) to refresh the value while the interface is open.'}, 'inputs': {'type': 'Component | list[Component] | set[Component] | None', 'default': 'None', 'description': None}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If True, the label is displayed; otherwise, it is hidden.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, the toggle is placed within a styled container for visual grouping and padding.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative sizing of the toggle in comparison to adjacent components when displayed in a row or block.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum width in pixels that the toggle will occupy, ensuring it does not shrink below this size.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, the toggle can be interacted with; if False, it is disabled. Default behavior is auto-detected based on usage.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the toggle is not rendered visibly in the interface.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'Optional identifier for the HTML element; useful for CSS customizations.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'Optional list of class names for the HTML element; useful for CSS customizations.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, the component is not rendered immediately, useful for deferred rendering or conditional UI updates.'}, 'key': {'type': 'int | str | None', 'default': 'None', 'description': 'if assigned, will be used to assume identity across a re-render. Components that have the same key across a re-render will have their value preserved.'}}, 'postprocess': {'value': {'type': 'bool | None', 'description': 'The toggle state to be returned.'}}, 'preprocess': {'return': {'type': 'bool | None', 'description': 'The toggle state as a boolean value.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the Toggle changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the Toggle.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the Toggle. Uses event data gradio.SelectData to carry `value` referring to the label of the Toggle, and `selected` to refer to state of the Toggle. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'Toggle': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_toggle`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_toggle/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_toggle"></a>  
</div>

A toggle component that represents a boolean value, allowing users to switch between True and False states. Can function both as an input, to capture user interaction, and as an output, to display a boolean state.
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_toggle
```

## Usage

```python
# Toggle - A Gradio Custom Component
# Created by Daniel Ialcin Misser Westergaard
# https://huggingface.co/dwancin
# https://github.com/dwancin
# (c) 2024

import gradio as gr
from gradio_toggle import Toggle

def update(input):
    output = input
    return output


with gr.Blocks() as demo:
    title = gr.HTML("<h1><center>gradio-toggle demo</center></h1>")
    with gr.Row():
        with gr.Column():
            input = Toggle(
                label="Input",
                value=False,
                info="Input version of the component",
                interactive=True,
            )
        with gr.Column():
            output = Toggle(
                label="Output",
                value=False,
                color="green",
                interactive=False,
            )
        
    input.change(fn=update, inputs=input, outputs=output)
        
if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `Toggle`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["Toggle"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["Toggle"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, the toggle state as a boolean value.
- **As output:** Should return, the toggle state to be returned.

 ```python
def predict(
    value: bool | None
) -> bool | None:
    return value
```
""", elem_classes=["md-custom", "Toggle-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          Toggle: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
