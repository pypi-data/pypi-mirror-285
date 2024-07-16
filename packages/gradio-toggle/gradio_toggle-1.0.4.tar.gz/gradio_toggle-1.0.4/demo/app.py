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
