function setQuestion(value) {
  document.getElementById("question").value = value;
}

function appendUserMessage(text) {
  const chatWindow = document.getElementById("chat-window");

  const wrapper = document.createElement("div");
  wrapper.className = "message user";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendAssistantMessage(answer, citations, latencyMs) {
  const chatWindow = document.getElementById("chat-window");

  const wrapper = document.createElement("div");
  wrapper.className = "message assistant";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const answerDiv = document.createElement("div");
  answerDiv.textContent = answer;
  bubble.appendChild(answerDiv);

  if (citations && citations.length > 0) {
    const sourcesBox = document.createElement("div");
    sourcesBox.className = "sources-box";

    const title = document.createElement("h4");
    title.textContent = "Sources";
    sourcesBox.appendChild(title);

    for (const citation of citations) {
      const source = document.createElement("div");
      source.className = "source-item";
      source.textContent = "• " + citation;
      sourcesBox.appendChild(source);
    }

    bubble.appendChild(sourcesBox);
  }

  const latency = document.createElement("div");
  latency.className = "latency";
  latency.textContent = `Latency: ${latencyMs} ms`;
  bubble.appendChild(latency);

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function askQuestion() {
  const input = document.getElementById("question");
  const errorEl = document.getElementById("error");
  const question = input.value.trim();

  errorEl.textContent = "";

  if (!question) {
    errorEl.textContent = "Please enter a question.";
    return;
  }

  appendUserMessage(question);
  input.value = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    const data = await response.json();

    if (!response.ok) {
      errorEl.textContent =
        data.error || "Server error while answering the question.";
      return;
    }

    appendAssistantMessage(data.answer, data.citations, data.latency_ms);
  } catch (err) {
    errorEl.textContent = "Unable to contact the assistant right now.";
  }
}

document.addEventListener("keydown", function (event) {
  const textarea = document.getElementById("question");
  if (event.key === "Enter" && !event.shiftKey && document.activeElement === textarea) {
    event.preventDefault();
    askQuestion();
  }
});