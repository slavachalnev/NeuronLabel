import os
import json
import openai

openai.api_key = os.environ["OAIKEY"]

def load_data_from_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def process_snippets_into_prompt(snippets):
    task_explanation = "Create a rule unifying the following snippets and determine if the rule is interpretable (say 'Interpretable') or not interpretable (say 'Not Interpretable')."

    processed_snippets = []
    for snippet in snippets:
        token_activation_pairs = snippet["token_activation_pairs"]
        max_activation = snippet["max_activation"]

        # Normalize activations by dividing by max_activation
        normalized_activations = [(token, activation / max_activation) for token, activation in token_activation_pairs]

        # Initialize variables to store token segments
        current_segment = []
        current_high_activation = normalized_activations[0][1] >= 0.8

        # Split tokens into segments based on activation levels
        for token, activation in normalized_activations:
            is_high_activation = activation >= 0.8

            # Check if the current token's activation level is different from the current segment's activation level
            if is_high_activation != current_high_activation:
                # Save the current segment
                segment_type = "HIGH:" if current_high_activation else "LOW:"
                processed_snippets.append(f"{segment_type}\n{''.join(current_segment)}")

                # Start a new segment with the current token
                current_segment = [token]
                current_high_activation = is_high_activation
            else:
                # Add the current token to the current segment
                current_segment.append(token)

        # Save the last segment
        segment_type = "HIGH:" if current_high_activation else "LOW:"
        processed_snippets.append(f"{segment_type}\n{''.join(current_segment)}")

    # Concatenate task explanation and processed snippets
    prompt = task_explanation + "\n\n" + "\n\n".join(processed_snippets) + "\n\n"
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
        print(f"Neuron {neuron['neuron_id']}: {gpt_response}")
        break

if __name__ == "__main__":
    main()

