# utils/summarizer.py
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load tokenizer and model once at start
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def generate_summary(text: str) -> str:
    """
    Generate a summary for the given text using T5 model.
    
    Args:
        text (str): Input text to summarize.
        
    Returns:
        str: Summarized text.
    """
    input_text = "summarize: " + text.strip().replace("\n", " ")
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

    outputs = model.generate(
        inputs.input_ids,
        max_length=150,
        min_length=30,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary
