
import gradio as gr
from gradio_uni_view_ocl import uni_view_ocl

with gr.Blocks() as demo:
    view = uni_view_ocl(smiles="[C@](S)(C)(N)O")
    btn = gr.Button('Update')
    def update_smiles():
        return uni_view_ocl(smiles="c1cc2ccccc2cc1")
    btn.click(update_smiles, outputs=view)
    btn1 = gr.Button('Print')
    def print_smiles(smiles):
        print(smiles)
    btn1.click(print_smiles, inputs=view)

if __name__ == "__main__":
    demo.launch()
