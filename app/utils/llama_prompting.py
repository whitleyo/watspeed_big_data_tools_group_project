import torch
from unsloth import FastLanguageModel # Uncomment and import if you are using Unsloth models
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

def gen_base_prompt(
    query_abstract: str,
    current_summary: str,
    abstract_i: str,
    new_abstract_title: str,
    new_abstract_doi: str,
    i: int
) -> str:
    """
    Generates the base prompt content for the summarization task.

    Args:
        query_abstract: The main abstract to which other abstracts are compared and summarized against.
        current_summary: The current consolidated summary.
        abstract_i: The text of the new abstract to integrate.
        new_abstract_title: The title of the new abstract.
        new_abstract_doi: The DOI of the new abstract.
        i: The rank (index) of the new abstract, used for numbering.

    Returns:
        A string containing the formatted base prompt.
    """
    return (
        "You are a scientific summarization assistant. Your task is to update an existing literature summary by integrating new information from a related abstract. "
        "Your output should be a concise, accurate combined summary that reflects both the original and new findings. Use clear scientific language and avoid redundancy. Strive for brevity and focus on integrating only the most crucial new information, especially if the current summary is already extensive.\n"
        "Your summary MUST follow this format: 'Introductory sentence; Fact1 [Title, DOI], Fact2 [Title, DOI], ...; (In conclusion|Overall|In summary).' Ensure all facts from *new* abstracts are cited using their respective Title and DOI. Facts from the *Query Abstract* should be cited as '[Query Abstract]. If a previous-summary is non-empty, incorporate facts for that summary with the references, without duplicating the query reference'.\n\n"
        "Here are several examples of how to perform this task:\n\n"
        "--- Example 1 ---\n"
        "Query Abstract: This study investigates the anti-inflammatory effects of drug X-123 in murine models, demonstrating significant reductions in cytokine levels and improved recovery times.\n"
        "Current Summary: Drug X-123 reduces inflammation in mice. [Drug X-123 reduces inflammation in murine models, 10.2000/j.example.2025.08.15]\n"
        "New Abstract: A related study found that X-123 also enhances tissue regeneration in rats by modulating macrophage activity and suppressing pro-inflammatory signaling pathways.\n"
        "New Abstract Title: X-123 also enhances tissue regeneration in rats through XXX macrophage pathway\n"
        "New Abstract DOI: 10.1000/j.example.2023.01.001\n"
        "Combined Summary: This summary integrates recent findings on drug X-123; Drug X-123 reduces inflammation in murine models [Query Abstract]. Another study found similar results where it reduced inflammation [Drug X-123 reduces inflammation in murine models, 10.2000/j.example.2025.08.15] and it also enhances tissue regeneration in rats by modulating macrophage activity and suppressing pro-inflammatory signaling pathways [X-123 also enhances tissue regeneration in rats through XXX macrophage pathway, 10.1000/j.example.2023.01.001]; In conclusion, X-123 shows multi-faceted effects.\n\n"
        "--- Example 2 ---\n"
        "Query Abstract: Researchers evaluated compound Y-456 for its effects on cognitive decline in elderly patients, noting improvements in memory retention and executive function over a 12-week trial.\n"
        "Current Summary: Compound Y-456 improves cognitive function in elderly patients.\n"
        "New Abstract: A follow-up study revealed that Y-456 also reduces oxidative stress in brain tissue and increases synaptic density in the hippocampus.\n"
        "New Abstract Title: Y-456's Impact on Cognitive Decline and Brain Health\n"
        "New Abstract DOI: 10.1000/j.example.2024.02.002\n"
        "Combined Summary: This update details further effects of compound Y-456; Compound Y-456 improves cognitive function in elderly patients, reduces oxidative stress in brain tissue, and increases synaptic density in the hippocampus [Y-456's Impact on Cognitive Decline and Brain Health, 10.1000/j.example.2024.02.002]; In conclusion, Y-456 has broad neurological benefits.\n\n"
        "--- Example 3 ---\n"
        "Query Abstract: The paper explores the role of protein Z in regulating insulin sensitivity in diabetic mice, showing enhanced glucose tolerance and reduced insulin resistance.\n"
        "Current Summary: An initial study indicated that protein Z regulates insulin sensitivity in diabetic mice, leading to enhanced glucose tolerance and reduced insulin resistance [Initial Protein Z Study, 10.1234/initial.study.2022.01.001].\n"
        "New Abstract: Additional research shows that protein Z also promotes glucose uptake in muscle cells and downregulates inflammatory markers associated with metabolic syndrome.\n"
        "New Abstract Title: Protein Z's Role in Glucose Metabolism and Inflammation\n"
        "New Abstract DOI: 10.1000/j.example.2025.03.003\n"
        "Combined Summary: This summary incorporates new data on protein Z; An initial study indicated that protein Z regulates insulin sensitivity in diabetic mice [Initial Protein Z Study, 10.1234/initial.study.2022.01.001], and additional research shows that protein Z also promotes glucose uptake in muscle cells and downregulates inflammatory markers associated with metabolic syndrome [Protein Z's Role in Glucose Metabolism and Inflammation, 10.1000/j.example.2025.03.003]; In conclusion, protein Z is a key metabolic regulator with multiple physiological effects.\n\n"
        "Now, perform the task with the following inputs:\n"
        f"Query Abstract: {query_abstract}\n"
        f"Current Summary: {current_summary}\n"
        f"New Abstract (ranked {i+1}th most similar to query): {abstract_i}\n"
        f"New Abstract Title: {new_abstract_title}\n"
        f"New Abstract DOI: {new_abstract_doi}\n\n"
        "Combined Summary:"
    )

def summarize_literature(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    query_abstract: str,
    top_k_abstracts: list[dict], # Assumed to have 'abstract', 'title', 'doi' keys
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    repetition_penalty: float = 1.0
) -> str:
    """
    Summarizes scientific literature by iteratively updating a summary based on new abstracts,
    handling both base and instruct models, with specific citation and format requirements.

    Args:
        model: The loaded Hugging Face model (e.g., from Unsloth's FastLanguageModel or AutoModelForCausalLM).
        tokenizer: The corresponding Hugging Face tokenizer.
        query_abstract: The main abstract to which other abstracts are compared and summarized against.
        top_k_abstracts: A list of dictionaries, where each dictionary contains 'abstract', 'title',
                         and 'doi' keys for the new abstract to integrate.
        max_new_tokens: Maximum number of tokens to generate for each summary update.
        temperature: Controls randomness in generation. Lower values make output more deterministic.
        repetition_penalty: Penalizes repeated tokens.

    Returns:
        The final consolidated summary of the literature.
    """
    current_summary = ""

    # Determine if it's an instruct model based on the presence of a chat template.
    is_instruct_model = hasattr(tokenizer, 'chat_template') and tokenizer.chat_template is not None
    print(f"🔄 Detected instruct model: {is_instruct_model}")

    # Apply Unsloth's inference optimization if the model is an instance of FastLanguageModel.
    try:
        if 'FastLanguageModel' in globals() and isinstance(model, FastLanguageModel):
            FastLanguageModel.for_inference(model)
    except NameError:
        print("💡 Unsloth's FastLanguageModel class not found. Skipping inference optimization specific to Unsloth.")
    except AttributeError:
        print("💡 Model object does not have 'for_inference' method. Skipping Unsloth inference optimization.")


    for i, doc in tqdm(enumerate(top_k_abstracts)):
        abstract_i = doc.get("abstract", "").strip()
        new_abstract_title = doc.get("title", "No Title Provided").strip()
        new_abstract_doi = doc.get("doi", "No DOI Provided").strip()

        if not abstract_i:
            continue

        # Generate the base prompt content using the new function
        base_prompt_content = gen_base_prompt(
            query_abstract=query_abstract,
            current_summary=current_summary,
            abstract_i=abstract_i,
            new_abstract_title=new_abstract_title,
            new_abstract_doi=new_abstract_doi,
            i=i
        )

        # Estimate initial prompt length using the base content for trimming decision.
        prompt_tokens_estimate = tokenizer(base_prompt_content, return_tensors="pt", truncation=False)["input_ids"][0]
        prompt_length_estimate = len(prompt_tokens_estimate)

        model_max_length = model.config.max_position_embeddings
        buffer_tokens = 32 # Buffer for generated tokens and potential tokenizer overhead

        total_length_needed = prompt_length_estimate + max_new_tokens + buffer_tokens

        # If the estimated length exceeds the model's max, trim the current summary.
        if total_length_needed > model_max_length:
            excess_tokens = total_length_needed - model_max_length
            print(f"⚠️ Prompt too long by {excess_tokens} tokens. Trimming current summary.")

            summary_tokens = tokenizer(current_summary, return_tensors="pt")["input_ids"][0]
            trim_amount = min(excess_tokens, len(summary_tokens))
            trimmed_summary_tokens = summary_tokens[trim_amount:] if trim_amount > 0 else torch.tensor([], dtype=torch.long)
            current_summary = tokenizer.decode(trimmed_summary_tokens, skip_special_tokens=True)
            print(f"📝 Trimmed summary length: {len(tokenizer(current_summary)['input_ids'])} tokens")

            # Rebuild the base_prompt_content with the now trimmed current_summary
            # This is critical as the prompt's content has changed.
            base_prompt_content = gen_base_prompt( # Recalculate with trimmed summary
                query_abstract=query_abstract,
                current_summary=current_summary,
                abstract_i=abstract_i,
                new_abstract_title=new_abstract_title,
                new_abstract_doi=new_abstract_doi,
                i=i
            )

        # Apply specific formatting based on model type (instruct vs. base)
        if is_instruct_model:
            messages = [
                {"role": "user", "content": base_prompt_content}
            ]
            formatted_prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            formatted_prompt = base_prompt_content

        inputs = tokenizer(formatted_prompt, return_tensors="pt", truncation=True).to(model.device)
        prompt_length = len(inputs["input_ids"][0])

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id
        )

        decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=False)

        if is_instruct_model:
            assistant_tag = "<|start_header_id|>assistant<|end_header_id|>\n"
            eot_tag = "<|eot_id|>"

            assistant_response_start_idx = decoded_output.rfind(assistant_tag)
            if assistant_response_start_idx != -1:
                temp_output = decoded_output[assistant_response_start_idx + len(assistant_tag):]
                eot_idx = temp_output.find(eot_tag)
                if eot_idx != -1:
                    generated_text = temp_output[:eot_idx].strip()
                else:
                    generated_text = temp_output.strip()
            else:
                print("⚠️ Warning: Assistant tag not found in instruct model output. Attempting general prompt removal.")
                if decoded_output.startswith(formatted_prompt):
                    generated_text = decoded_output[len(formatted_prompt):].strip()
                else:
                    generated_text = decoded_output.strip()
        else:
            if decoded_output.startswith(formatted_prompt):
                generated_text = decoded_output[len(formatted_prompt):].strip()
            else:
                generated_text = decoded_output.strip()

        # print(f"\n--- Iteration {i+1} ---")
        # print(f"Prompt token count: {prompt_length}")
        # print(f"Generated token count: {len(tokenizer(generated_text)['input_ids'])}")
        # print("Generated text:\n", generated_text)

        current_summary = generated_text.strip()

    return current_summary

