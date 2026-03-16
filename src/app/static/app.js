let pipelineReady = false;

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

async function safeJson(response) {
  const text = await response.text();

  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch (err) {
    throw new Error(`Server returned non-JSON response: ${text.slice(0, 200)}`);
  }
}

async function checkHealth() {
  const response = await fetch("/health");
  return await safeJson(response);
}

async function warmupPipeline() {
  const errorEl = document.getElementById("error");
  errorEl.textContent = "Assistant is warming up...";

  const response = await fetch("/warmup", {
    method: "POST"
  });

  const data = await safeJson(response);

  if (!response.ok && response.status !== 202) {
    throw new Error(data.pipeline_error || data.error || "Warmup failed.");
  }

  if (data.pipeline_ready || data.status === "ready") {
    pipelineReady = true;
    errorEl.textContent = "";
    return;
  }

  if (response.status === 202 || data.status === "loading") {
    await waitUntilReady();
    return;
  }
}

async function waitUntilReady(maxAttempts = 60, delayMs = 5000) {
  const errorEl = document.getElementById("error");

  for (let i = 0; i < maxAttempts; i++) {
    const health = await checkHealth();

    if (health.pipeline_ready) {
      pipelineReady = true;
      errorEl.textContent = "";
      return true;
    }

    if (health.pipeline_error) {
      errorEl.textContent = `Pipeline error: ${health.pipeline_error}`;
      return false;
    }

    errorEl.textContent = "Assistant is warming up...";
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }

  errorEl.textContent = "Warmup is taking longer than expected. Please try again.";
  return false;
}

async function ensurePipelineReady() {
  if (pipelineReady) {
    return true;
  }

  try {
    const health = await checkHealth();

    if (health.pipeline_ready) {
      pipelineReady = true;
      return true;
    }

    await warmupPipeline();

    const finalHealth = await checkHealth();
    pipelineReady = !!finalHealth.pipeline_ready;
    return pipelineReady;
  } catch (err) {
    document.getElementById("error").textContent =
      err.message || "Unable to warm up the assistant.";
    return false;
  }
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

  const ready = await ensurePipelineReady();
  if (!ready) {
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

    const data = await safeJson(response);

    if (!response.ok) {
      errorEl.textContent =
        data.error || "Server error while answering the question.";
      return;
    }

    appendAssistantMessage(data.answer, data.citations, data.latency_ms);
  } catch (err) {
    errorEl.textContent = err.message || "Unable to contact the assistant right now.";
    console.error(err);
  }
}

document.addEventListener("keydown", function (event) {
  const textarea = document.getElementById("question");
  if (event.key === "Enter" && !event.shiftKey && document.activeElement === textarea) {
    event.preventDefault();
    askQuestion();
  }
});