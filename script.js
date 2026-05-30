// ── Document Extraction Feature ──────────────────────────────────────────────

// Make drop area clickable to select file
dropArea.addEventListener("click", () => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".pdf,.png,.jpg,.jpeg,.docx";
  input.onchange = (e) => handleFile(e.target.files[0]);
  input.click();
});

// Handle dropped file
dropArea.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

async function handleFile(file) {
  // Show uploading state
  dropArea.innerHTML = `
    <i class="fa-solid fa-spinner fa-spin"></i>
    <h3>Extracting Details...</h3>
    <p>${file.name}</p>
  `;

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:5000/extract", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      showExtractedFields(data.extracted_fields);
      dropArea.innerHTML = `
        <i class="fa-solid fa-circle-check" style="color:#00c6ff"></i>
        <h3>Extraction Complete!</h3>
        <p>${file.name}</p>
      `;
    } else {
      dropArea.innerHTML = `
        <i class="fa-solid fa-circle-xmark" style="color:red"></i>
        <h3>Error: ${data.error}</h3>
        <p>Try again</p>
      `;
    }
  } catch (err) {
    dropArea.innerHTML = `
      <i class="fa-solid fa-circle-xmark" style="color:red"></i>
      <h3>Server not running!</h3>
      <p>Start extract.py first</p>
    `;
  }
}

function showExtractedFields(fields) {
  // Remove old results if any
  const existing = document.getElementById("extractionResults");
  if (existing) existing.remove();

  // Filter out null/empty fields
  const validFields = Object.entries(fields).filter(
    ([_, v]) => v && v !== "null" && v !== ""
  );

  // Build results HTML
  const resultsHTML = validFields.map(([key, value]) => `
    <div class="verify-card glass">
      <h3>${formatKey(key)}</h3>
      <p>${value}</p>
      <span class="success">✅ Extracted</span>
    </div>
  `).join("");

  // Inject into verification section
  const verifyGrid = document.querySelector(".verify-grid");
  
  const resultsSection = document.createElement("div");
  resultsSection.id = "extractionResults";
  resultsSection.innerHTML = `
    <h2 class="section-title" style="margin-top:2rem">📄 Extracted Loan Details</h2>
    <div class="verify-grid">${resultsHTML}</div>
  `;

  verifyGrid.parentElement.appendChild(resultsSection);

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: "smooth" });
}

function formatKey(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
