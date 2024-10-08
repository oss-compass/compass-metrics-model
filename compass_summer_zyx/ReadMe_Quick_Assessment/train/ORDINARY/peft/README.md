
  Accuracy |
| --------- | ---- |
| Human baseline (crowdsourced) |	0.897 |
| Flan-T5 | 0.892 |
| lora-t0-3b | 0.863 |



Quantization is another method for reducing the memory requirements of a model by representing the data in a lower precision. It can be combined with PEFT methods to make it even easier to train and load LLMs for inference.

* Learn how to finetune [meta-llama/Llama-2-7b-hf](https://huggingface.co/meta-llama/Llama-2-7b-hf) with QLoRA and the [TRL](https://huggingface.co/docs/trl/index) library on a 16GB GPU in the [Finetune LLMs on your own consumer hardware using tools from PyTorch and Hugging Face ecosystem](https://pytorch.org/blog/finetune-llms/) blog post.
* Learn how to finetune a [openai/whisper-large-v2](https://huggingface.co/openai/whisper-large-v2) model for multilingual automatic speech recognition with LoRA and 8-bit quantization in this [notebook](https://colab.research.google.com/drive/1DOkD_5OUjFa0r5Ik3SgywJLJtEo2qLxO?usp=sharing) (see this [notebook](https://colab.research.google.com/drive/1vhF8yueFqha3Y3CpTHN6q9EVcII9EYzs?usp=sharing) instead for an example of streaming a dataset).




Use this [Space](https://stevhliu-peft-methods.hf.space) or check out the [docs](https://huggingface.co/docs/peft/main/en/index) to find which models officially support a PEFT method out of the box. Even if you don't see a model listed below, you can manually configure the model config to enable PEFT for a model. Read the [New transformers architecture](https://huggingface.co/docs/peft/main/en/developer_guides/custom_models#new-transformers-architectures) guide to learn how.

## Contribute

If you would like to contribute to PEFT, please check out our [contribution guide](https://huggingface.co/docs/peft/developer_guides/contributing).

## Citing 🤗 PEFT

To use 🤗 PEFT in your publication, please cite it by using the following BibTeX entry.

```bibtex
@Misc{peft,
  title =        {PEFT: State-of-the-art Parameter-Efficient Fine-Tuning methods},
  author =       {Sourab Mangrulkar and Sylvain Gugger and Lysandre Debut and Younes Belkada and Sayak Paul and Benjamin Bossan},
  howpublished = {\url{https://github.com/huggingface/peft}},
  year =         {2022}
}
```