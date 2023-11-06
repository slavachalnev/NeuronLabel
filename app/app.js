const snippetsContainer = document.getElementById("snippets-container");
const interpretableButton = document.getElementById("interpretable");
const notInterpretableButton = document.getElementById("not-interpretable");

// Fetch the JSON data
let data;
fetch("data.json")
  .then((response) => response.json())
  .then((jsonData) => {
    data = jsonData;
    renderSnippets();
  })
  .catch((error) => {
    console.error("Error loading data.json:", error);
  });


let currentNeuronIndex = 0;

function displaySnippets(snippets, neuronId) {
  snippets.forEach((snippet) => {
    const snippetDiv = document.createElement("div");
    snippetDiv.className = "snippet";

    // Create and append the neuron ID element
    const neuronIdElement = document.createElement("div");
    neuronIdElement.className = "neuron-id";
    neuronIdElement.textContent = `Neuron ID: ${neuronId}`;
    snippetDiv.appendChild(neuronIdElement);

    // Create and append the max activation element
    const maxActivation = snippet.max_activation;
    const maxActivationElement = document.createElement("div");
    maxActivationElement.className = "max-activation";
    maxActivationElement.textContent = `Max Activation: ${maxActivation}`;
    snippetDiv.appendChild(maxActivationElement);

    // spacing
    const spacingElement = document.createElement("div");
    spacingElement.className = "spacing";
    snippetDiv.appendChild(spacingElement);

    // Existing code for token_activation_pairs
    snippet.token_activation_pairs.forEach(([token, activation]) => {
      const normalizedActivation = activation / maxActivation;
      const tokenElement = document.createElement("span");
      tokenElement.className = "token";
      tokenElement.style.backgroundColor = `rgba(255, 0, 0, ${normalizedActivation})`;
      tokenElement.textContent = token;
      snippetDiv.appendChild(tokenElement);
    });

    snippetsContainer.appendChild(snippetDiv);
  });
}



function nextNeuron() {
  currentNeuronIndex++;
  renderSnippets();
}

interpretableButton.addEventListener("click", () => {
  saveResult("Interpretable");
  nextNeuron();
});

notInterpretableButton.addEventListener("click", () => {
  saveResult("Not Interpretable");
  nextNeuron();
});

const downloadResultsButton = document.getElementById("download-results");
downloadResultsButton.addEventListener("click", () => {
  downloadResults();
});

function saveResult(choice) {
  const result = {
    neuron_id: Object.keys(data)[currentNeuronIndex],
    choice: choice,
  };

  const resultsKey = "neuron_results";
  let results = JSON.parse(localStorage.getItem(resultsKey) || "[]");
  results.push(result);
  localStorage.setItem(resultsKey, JSON.stringify(results));
}

function downloadResults() {
  const resultsKey = "neuron_results";
  const results = JSON.parse(localStorage.getItem(resultsKey) || "[]");

  const a = document.createElement("a");
  a.href = URL.createObjectURL(
    new Blob([JSON.stringify(results, null, 2)], { type: "application/json" })
  );
  a.download = "results.json";
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function renderSnippets() {
  snippetsContainer.innerHTML = ""; // Clear the snippets container

  if (currentNeuronIndex >= Object.keys(data).length) {
    alert("All neurons have been evaluated.");
    return;
  }

  const neuronId = Object.keys(data)[currentNeuronIndex];
  const neuron_name = data[neuronId].neuron_id;
  displaySnippets(data[neuronId].snippets, neuron_name);
}

const clearResultsButton = document.getElementById("clear-results");
clearResultsButton.addEventListener("click", () => {
  clearResults();
});

function clearResults() {
  localStorage.removeItem("neuron_results");
  alert("Results history cleared.");
}

renderSnippets();