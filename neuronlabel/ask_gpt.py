import os
import json
import openai

openai.api_key = os.environ["OAIKEY"]


TASK_EXPLANATION = "Create a rule unifying the following snippets and determine if the rule \
explains most of the snippets (say 'EXPLAINS') or does not explain most of the snippets (say 'DOES NOT EXPLAIN') \n\n\
The text is split into HIGH TOKENS (the rule should explain these) LOW TOKENS (the rule should not explain these). \
The snippets are separated by -----.\n\n\
The output should be of the form:\n\n[RULE]\n[EXPLAINS/DOES NOT EXPLAIN]"


def load_data_from_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def process_snippet(snippet):
    token_activation_pairs = snippet["token_activation_pairs"]
    max_activation = snippet["max_activation"]

    # Normalize activations by dividing by max_activation
    normalized_activations = [(token, activation / max_activation) for token, activation in token_activation_pairs]

    # Split tokens into segments based on activation levels
    segments = []
    current_segment = {"type": None, "tokens": []}

    for token, activation in normalized_activations:
        segment_type = "HIGH TOKENS" if activation >= 0.8 else "LOW TOKENS"

        if current_segment["type"] != segment_type:
            if current_segment["tokens"]:
                segments.append(current_segment)
            current_segment = {"type": segment_type, "tokens": []}

        current_segment["tokens"].append(token)

    if current_segment["tokens"]:
        segments.append(current_segment)

    return "\n-----\n"+"\n\n".join([f"{segment['type']}\n{''.join(segment['tokens'])}" for segment in segments]) + "\n"

def process_snippets_into_prompt(snippets):
    processed_snippets = [process_snippet(snippet) for snippet in snippets]
    prompt = f"{TASK_EXPLANATION}\n\n{''.join(processed_snippets)}\n\n [RULE]\n"
    return prompt


def call_gpt_api(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def main():
    json_file_path = "../solu-4l.json"
    data = load_data_from_json(json_file_path)

    for neuron in data:
        snippets = neuron["snippets"]
        prompt = process_snippets_into_prompt(snippets)
        gpt_response = call_gpt_api(prompt)
        print(f"Neuron {neuron['neuron_id']}:\n{gpt_response}")
        print()

if __name__ == "__main__":
    main()

