# import necessary libraries
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
def llama_prompting_loop(
    model,
    tokenizer,
    data_loader,
    idx_use,
    device,
    max_length=512,
    temperature=0.7,
    top_p=0.9,
):
    prompt_template = """
    Given the following running literature summary, update the summary with the new abstract I give you.
    If the summary is empty, initialize summary with summary of the abstract.
    If summary is not empty, keep the knowledge of the prior summary to the extent possible,
    but update the summary given the content of the new abstract.

    Summary: {}
    Abstract: {}

    """
    # batch size should be 1. Max chars supported right now is 2048
    # check that batch size is 1
    if data_loader.batch_size != 1:
        raise ValueError("DataLoader batch size must be 1 for this function to work correctly.")
    # data loader should support integer indexing
    if not hasattr(data_loader, '__getitem__'):
        raise ValueError("DataLoader must support indexing to use this function.")
    for batch in data_loader:
        abstracts = batch["text"]
        summaries = batch["summary"] if "summary" in batch else ["" for _ in abstracts]

        for abstract, summary in zip(abstracts, summaries):
            prompt = prompt_template.format(summary, abstract)
            inputs = tokenizer(prompt, return_tensors="pt", max_length=max_length, truncation=True).to(device)

            outputs = model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True
            )

            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Generated Summary: {generated_text}")

