# NeuronLabel
Neuron Label is a simple tool for visually analyzing and labeling the interpretability of neurons in a neural network. The tool displays text snippets with activated tokens highlighted in varying shades of red based on their activation values. Users can label neurons as "Interpretable" or "Not Interpretable" and download the results in a JSON format.


## Setup
1. Clone the repository or download the source code.
2. Ensure you have a properly formatted data.json file.

## Usage
1. Run with `python serve.py /path/to/data.json`
2. Go to http://localhost:8000

## Data Format
The data.json file should have the following format:

```json
{
  "neuron_id": [
    {
      "text": "example text snippet",
      "max_activation": 2.3037002086639404,
      "token_activation_pairs": [
        [
          "token1",
          0.1
        ],
        [
          "token2",
          0.5
        ],
        ...
      ]
    },
    ...
  ]
}
```

`neuron_id` is the identifier of the neuron, and each `neuron_id` has an array of text snippets associated with it. Each text snippet object contains the following properties:

- `text`: The text snippet itself.
- `max_activation`: The maximum activation value of the neuron for this snippet.
- `token_activation_pairs`: An array of pairs, where each pair consists of a token and its corresponding activation value.

