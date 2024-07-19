
import gradio as gr
from gradio_sequence_editor import sequence_editor


with gr.Blocks() as demo:
    sequence = sequence_editor()
    print_btn = gr.Button('Print')
    def print_sequence():
        return sequence_editor(sequences="ABCDE")
    print_btn.click(print_sequence, outputs=sequence)

if __name__ == "__main__":
    demo.launch()
