const snippetsContainer = document.getElementById("snippets-container");
const interpretableButton = document.getElementById("interpretable");
const notInterpretableButton = document.getElementById("not-interpretable");

// Replace this with the actual JSON data.
const data = [
  {
    "neuron_id": 1,
    "snippets": [
      {
        "tokens": ["This", " is", " a", " text", " snippet", " with", " an", " activated", " token."],
        "activations": [0, 0, 0.5, 0, 0, 0, 0, 0, 0]
      },
      {
        "tokens": ["A", " different", " activated", " token."],
        "activations": [0, 0.8, 0.5, 0]
      }
    ]
  },
  {
    "neuron_id": 2,
    "snippets": [
      {
        "tokens": ["la", "la", "la"],
        "activations": [0.2, 0, 0.5]
      }
    ]
  }
];

function displaySnippets(snippets) {
  snippets.forEach((snippet) => {
    const snippetDiv = document.createElement("div");
    snippetDiv.className = "snippet";

    snippet.tokens.forEach((token, index) => {
      const tokenElement = document.createElement("span");
      tokenElement.className = "token";
      tokenElement.style.backgroundColor = `rgba(255, 0, 0, ${snippet.activations[index]})`;
      tokenElement.textContent = token;
      snippetDiv.appendChild(tokenElement);
    });

    snippetsContainer.appendChild(snippetDiv);
  });
}

interpretableButton.addEventListener("click", () => {
  saveResult("Interpretable");
});

notInterpretableButton.addEventListener("click", () => {
  saveResult("Not Interpretable");
});

const downloadResultsButton = document.getElementById("download-results");
downloadResultsButton.addEventListener("click", () => {
  downloadResults();
});

function saveResult(choice) {
  const result = {
    neuron_id: data[0].neuron_id,
    choice: choice
  };

  const resultsKey = 'neuron_results';
  let results = JSON.parse(localStorage.getItem(resultsKey) || '[]');
  results.push(result);
  localStorage.setItem(resultsKey, JSON.stringify(results));
}

function downloadResults() {
  const resultsKey = 'neuron_results';
  const results = JSON.parse(localStorage.getItem(resultsKey) || '[]');

  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(results, null, 2)], { type: "application/json" }));
  a.download = "results.json";
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

displaySnippets(data[0].snippets);
