const form = document.querySelector("#analyze-form");
const result = document.querySelector("#result");
const submitButton = document.querySelector("#submit-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = true;
  result.className = "result";
  submitButton.disabled = true;
  submitButton.querySelector("span").textContent = "Analyzing…";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: document.querySelector("#subject").value,
        body: document.querySelector("#body").value,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "The email could not be analyzed.");
    }

    result.classList.toggle("result-safe", data.label === 0);
    const description = data.label === 1
      ? "This email resembles examples labeled phishing in the dataset."
      : "This email resembles examples labeled not phishing in the dataset.";
    result.replaceChildren();

    const message = document.createElement("div");
    const heading = document.createElement("h3");
    const detail = document.createElement("p");
    const confidence = document.createElement("span");
    heading.textContent = `Result: ${data.verdict}`;
    detail.textContent = description;
    confidence.className = "confidence";
    confidence.textContent = `${data.confidence}% model score`;
    message.append(heading, detail);
    result.append(message, confidence);
    result.hidden = false;
  } catch (error) {
    result.className = "result";
    const message = document.createElement("p");
    message.className = "error-message";
    message.textContent = error.message;
    result.replaceChildren(message);
    result.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.querySelector("span").textContent = "Analyze email";
  }
});

const searchInput = document.querySelector("#email-search");
const labelFilter = document.querySelector("#label-filter");
const rows = [...document.querySelectorAll("#email-rows tr[data-label]")];
const emptyState = document.querySelector("#empty-state");

function filterEmails() {
  const query = searchInput.value.trim().toLowerCase();
  const label = labelFilter.value;
  let visibleCount = 0;

  for (const row of rows) {
    const matchesQuery = row.dataset.search.includes(query);
    const matchesLabel = label === "all" || row.dataset.label === label;
    row.hidden = !(matchesQuery && matchesLabel);
    if (!row.hidden) visibleCount += 1;
  }
  emptyState.hidden = visibleCount > 0;
}

searchInput.addEventListener("input", filterEmails);
labelFilter.addEventListener("change", filterEmails);
