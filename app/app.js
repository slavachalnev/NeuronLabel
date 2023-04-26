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

function displaySnippets(snippets) {
  snippets.forEach((snippet) => {
    const snippetDiv = document.createElement("div");
    snippetDiv.className = "snippet";

    const maxActivation = snippet.max_activation;

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

  if (currentNeuronIndex >= data.length) {
    alert("All neurons have been evaluated.");
    return;
  }

  displaySnippets(data[currentNeuronIndex].snippets);
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