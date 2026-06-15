const form = document.querySelector('#compareForm');
const statusEl = document.querySelector('#status');
const submitButton = document.querySelector('#submitButton');
const results = document.querySelector('#results');

function setupPreview(inputName, previewId) {
  const input = document.querySelector(`input[name="${inputName}"]`);
  const preview = document.querySelector(previewId);

  input.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) return;
    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';
  });
}

function renderDifferences(items) {
  const container = document.querySelector('#differences');
  container.innerHTML = '';

  if (!items?.length) {
    container.textContent = 'No visible differences were identified.';
    return;
  }

  items.forEach((item) => {
    const div = document.createElement('div');
    div.className = 'result-item';
    div.innerHTML = `
      <h3>${item.area}</h3>
      <p><strong>Image 1:</strong> ${item.image_1_observation}</p>
      <p><strong>Image 2:</strong> ${item.image_2_observation}</p>
      <p><strong>Severity:</strong> ${item.severity}</p>
    `;
    container.appendChild(div);
  });
}

function renderMaintenance(items) {
  const container = document.querySelector('#maintenanceReport');
  container.innerHTML = '';

  if (!items?.length) {
    container.textContent = 'No maintenance actions were recommended.';
    return;
  }

  items.forEach((item) => {
    const div = document.createElement('div');
    div.className = 'result-item';
    div.innerHTML = `
      <h3>${item.issue}</h3>
      <p>${item.recommendation}</p>
      <p><strong>Priority:</strong> ${item.priority}</p>
    `;
    container.appendChild(div);
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  submitButton.disabled = true;
  statusEl.textContent = 'Comparing images...';
  results.classList.add('hidden');

  try {
    const response = await fetch('/compare', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Comparison failed.');

    document.querySelector('#summary').textContent = data.summary;
    renderDifferences(data.differences);

    const confidence = Number(data.confidence || 0);
    document.querySelector('#confidenceBar').value = confidence;
    document.querySelector('#confidenceText').textContent = `${Math.round(confidence * 100)}%`;
    document.querySelector('#limitations').textContent = data.limitations || '';

    renderMaintenance(data.maintenance_report);
    results.classList.remove('hidden');
    statusEl.textContent = 'Done.';
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

setupPreview('image1', '#preview1');
setupPreview('image2', '#preview2');
