import torch
import random
import json
from torch.utils.data import DataLoader
from typing import List, Dict, Tuple

from tqdm import tqdm

import torch.nn as nn
import numpy as np

from datasets import load_dataset

import transformer_lens
from transformer_lens import HookedTransformer
from transformer_lens import utils as tutils


def get_top_examples(model, dataset_loader, neurons: List[int], k: int):
    d_mlp = model.cfg.d_mlp
    n_neurons = len(neurons)
    acts_cache = [None for _ in range(len(model.blocks))]

    def get_activation_hook(layer):
        # neurons from d_mlp*layer to d_mlp*(layer+1)
        selected_for_layer = [n for n in neurons if n >= d_mlp*layer and n < d_mlp*(layer+1)]
        selected_for_layer = [n - d_mlp*layer for n in selected_for_layer]

        def hook(value, hook):
            acts_cache[layer] = value[:, :, selected_for_layer].detach().cpu() # shape is (batch_size, seq_len, n_neurons)
            return value

        return hook

    fwd_hooks = []
    for layer in range(len(model.blocks)):
        fwd_hooks.append((f"blocks.{layer}.mlp.hook_post", get_activation_hook(layer)))

    best_so_far = [[] for _ in range(n_neurons)] # list of lists of {neuron, activations, tokens, max_activation}
    for batch_idx, batch in tqdm(enumerate(dataset_loader)):

        with model.hooks(fwd_hooks=fwd_hooks), torch.no_grad():
            model(batch["tokens"], return_type="loss")
        
        # stack activations from all layers
        batch_activations = torch.cat(acts_cache, dim=2) # shape is (batch_size, seq_len, n_neurons)

        for i, example in enumerate(batch["tokens"]):
            for j, neuron in enumerate(neurons):
                d = {
                    "neuron": neuron,
                    "activations": batch_activations[i, :, j],
                    "tokens": example,
                    "max_activation": torch.max(batch_activations[i, :, j]).item(),
                }
                best_so_far[j].append(d)
        
        # keep only top k activations
        for j in range(n_neurons):
            best_so_far[j] = sorted(best_so_far[j], key=lambda x: x["max_activation"], reverse=True)[:k]
        
    return best_so_far


def extract_chunk(tokens, activations, chunk_size=100):
    max_index = activations.index(max(activations))
    start = max(0, max_index - chunk_size // 2)
    end = min(len(tokens), max_index + chunk_size // 2)
    return tokens[start:end], activations[start:end]


def store_results_to_json(best_examples: List[List[Dict]], tokenizer, filename: str):
    """
    Stores the top k activations for each neuron along with the corresponding input tokens in a JSON file.
    """

    results = []
    for neuron_best_examples in best_examples:
        snippets = []
        for example in neuron_best_examples:
            neuron = example["neuron"]
            tokens = example["tokens"]
            activations = example["activations"].tolist()
            max_activation = example["max_activation"]

            # Extract the chunk of tokens and activations around the max activation token
            chunk_tokens, chunk_activations = extract_chunk(tokens, activations)

            # Decode the chunk of tokens to text
            tokens_text = tokenizer.decode(chunk_tokens)

            # Create token-activation pairs for the chunk of tokens and activations
            token_activation_pairs = [(tokenizer.decode(token), activation) for token, activation in zip(chunk_tokens, chunk_activations)]

            snippets.append({
                "text": tokens_text,
                "max_activation": max_activation,
                "token_activation_pairs": token_activation_pairs
            })

        results.append({
            "neuron_id": str(neuron),
            "snippets": snippets
        })

    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)


def main(model, dataset_loader, save_path):
    num_neurons = 100
    total_neurons = model.cfg.d_mlp * len(model.blocks)
    top_k = 20

    selected_neurons = random.sample(range(total_neurons), num_neurons)
    top_k_examples = get_top_examples(model, dataset_loader, selected_neurons, top_k)
    store_results_to_json(best_examples=top_k_examples, tokenizer=tokenizer, filename=save_path)

if __name__ == "__main__":
    model_name = "solu-4l"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = HookedTransformer.from_pretrained(model_name, device=device)

    tokenizer = model.tokenizer
    # dataset_loader = big_data_loader(tokenizer=tokenizer, batch_size=8, big=False)

    data = load_dataset("NeelNanda/pile-10k", split="train")
    dataset = tutils.tokenize_and_concatenate(data, tokenizer)
    dataset_loader = DataLoader(dataset, batch_size=8, shuffle=True, drop_last=True)

    main(model, dataset_loader, save_path=f"{model_name}.json")
