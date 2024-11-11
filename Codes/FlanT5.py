import torch
# print(torch.__version__)
# print(torch.tensor([1.0, 2.0, 3.0]))

from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the FLAN-T5 model and tokenizer
model_name = "google/flan-t5-large"  # You can use 'flan-t5-small', 'flan-t5-base', 'flan-t5-large', etc.
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
