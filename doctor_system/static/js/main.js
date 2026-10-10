/**
 * AcuMeds Doctor Portal - Client-Side Interactive Helpers
 */

document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss flash alerts after 5s
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    });
  }, 5000);

  // Dynamic Prescription Row Builder
  const addMedBtn = document.getElementById('add-med-btn');
  const medTableBody = document.getElementById('prescribed-meds-body');

  if (addMedBtn && medTableBody) {
    addMedBtn.addEventListener('click', function () {
      const rowId = Date.now();
      const tr = document.createElement('tr');
      tr.className = 'med-row';
      tr.innerHTML = `
        <td>
          <input type="text" name="med_name[]" class="form-control med-name-input" placeholder="Search medicine..." required autocomplete="off">
          <input type="hidden" name="med_id[]" class="med-id-input">
          <div class="autocomplete-dropdown" style="position:relative;"></div>
        </td>
        <td>
          <input type="text" name="med_dosage[]" class="form-control" placeholder="e.g. 500 mg" value="500 mg">
        </td>
        <td>
          <select name="med_frequency[]" class="form-control">
            <option value="1-0-1 (Twice daily)">1-0-1 (Twice daily)</option>
            <option value="1-1-1 (Thrice daily)">1-1-1 (Thrice daily)</option>
            <option value="1-0-0 (Once Morning)">1-0-0 (Morning)</option>
            <option value="0-0-1 (Once Night)">0-0-1 (Night)</option>
            <option value="SOS (As needed)">SOS (As needed)</option>
          </select>
        </td>
        <td>
          <select name="med_timing[]" class="form-control">
            <option value="After Food">After Food</option>
            <option value="Before Food">Before Food</option>
            <option value="With Food">With Food</option>
          </select>
        </td>
        <td>
          <input type="text" name="med_duration[]" class="form-control" placeholder="e.g. 5 Days" value="5 Days">
        </td>
        <td>
          <input type="number" name="med_qty[]" class="form-control" value="1" min="1" style="width: 70px;">
        </td>
        <td>
          <button type="button" class="btn btn-sm btn-danger remove-med-btn" style="background: #fee2e2; color: #dc2626; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer;">✕</button>
        </td>
      `;
      medTableBody.appendChild(tr);
      attachAutocomplete(tr.querySelector('.med-name-input'));
    });

    // Delegate remove row event
    medTableBody.addEventListener('click', function (e) {
      if (e.target && e.target.classList.contains('remove-med-btn')) {
        const row = e.target.closest('tr');
        if (medTableBody.querySelectorAll('tr').length > 1) {
          row.remove();
        } else {
          alert('At least one medicine is required.');
        }
      }
    });

    // Attach autocomplete to existing inputs
    document.querySelectorAll('.med-name-input').forEach(attachAutocomplete);
  }

  // Autocomplete Medicine Search from AcuMeds Shared Inventory
  function attachAutocomplete(input) {
    if (!input) return;
    let timeout = null;

    input.addEventListener('input', function () {
      clearTimeout(timeout);
      const query = input.value.trim();
      const parent = input.parentElement;
      let dropdown = parent.querySelector('.autocomplete-dropdown');

      if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'autocomplete-dropdown';
        dropdown.style.cssText = 'position: absolute; left: 0; right: 0; background: white; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 1000; max-height: 200px; overflow-y: auto;';
        parent.style.position = 'relative';
        parent.appendChild(dropdown);
      }

      if (query.length < 2) {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
        return;
      }

      timeout = setTimeout(function () {
        fetch(`/api/medicines/search?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            dropdown.innerHTML = '';
            if (data.length === 0) {
              dropdown.style.display = 'none';
              return;
            }

            data.forEach(item => {
              const div = document.createElement('div');
              div.style.cssText = 'padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;';
              div.innerHTML = `
                <div>
                  <strong>${item.name}</strong> <span style="font-size: 0.75rem; color: #0f766e; background: #ccfbf1; padding: 2px 6px; border-radius: 12px;">${item.strength || item.category}</span>
                </div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #0f172a;">₹${item.price}</div>
              `;

              div.addEventListener('mouseenter', () => div.style.background = '#f8fafc');
              div.addEventListener('mouseleave', () => div.style.background = 'white');

              div.addEventListener('click', function () {
                input.value = item.name;
                const row = input.closest('tr');
                if (row) {
                  const idInput = row.querySelector('.med-id-input');
                  if (idInput) idInput.value = item.id;
                  if (item.strength) {
                    const dosageInput = row.querySelector('input[name="med_dosage[]"]');
                    if (dosageInput) dosageInput.value = item.strength;
                  }
                }
                dropdown.innerHTML = '';
                dropdown.style.display = 'none';
              });

              dropdown.appendChild(div);
            });
            dropdown.style.display = 'block';
          })
          .catch(err => console.error('Medicine search error:', err));
      }, 250);
    });

    document.addEventListener('click', function (e) {
      if (!input.contains(e.target)) {
        const dropdown = input.parentElement.querySelector('.autocomplete-dropdown');
        if (dropdown) dropdown.style.display = 'none';
      }
    });
  }

  // AI Diagnosis Clinical Assistant
  const aiBtn = document.getElementById('run-ai-diagnosis-btn');
  const aiResultBox = document.getElementById('ai-diagnosis-results');

  if (aiBtn && aiResultBox) {
    aiBtn.addEventListener('click', function () {
      const symptoms = document.getElementById('patient-symptoms-text')?.value || document.getElementById('consult-symptoms')?.innerText || '';
      const age = document.getElementById('patient-age')?.value || '';
      const gender = document.getElementById('patient-gender')?.value || '';
      const bp = document.getElementById('vitals-bp')?.value || '';

      if (!symptoms.trim()) {
        alert('Please ensure patient symptoms are recorded to trigger AI diagnosis.');
        return;
      }

      aiBtn.disabled = true;
      aiBtn.innerHTML = '<span>⚡ Analyzing symptoms with AI...</span>';
      aiResultBox.style.display = 'block';
      aiResultBox.innerHTML = '<div style="padding: 16px; text-align: center; color: #0f766e;"><strong>Evaluating clinical parameters & pharmacology databases...</strong></div>';

      fetch('/api/ai-diagnosis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms: symptoms,
          age: age,
          gender: gender,
          vitals: bp ? `BP: ${bp}` : ''
        })
      })
      .then(res => res.json())
      .then(data => {
        aiBtn.disabled = false;
        aiBtn.innerHTML = '<span>✨ AI Clinical Diagnosis</span>';

        if (data.analysis) {
          // Render markdown-like simple formatting
          let formatted = data.analysis
            .replace(/### (.*?)\n/g, '<h3 style="color: #0f766e; margin-top: 10px; font-size: 1.05rem;">$1</h3>')
            .replace(/#### (.*?)\n/g, '<h4 style="color: #0f172a; margin-top: 8px; font-size: 0.95rem;">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n- /g, '<br>• ')
            .replace(/\n/g, '<br>');

          aiResultBox.innerHTML = `
            <div style="background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 12px; padding: 20px; color: #0f172a; line-height: 1.6;">
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ccfbf1; padding-bottom: 8px; margin-bottom: 12px;">
                <span style="font-weight: 700; color: #0f766e; font-size: 0.85rem; text-transform: uppercase;">AcuMeds Clinical Decision Support System</span>
                <span style="font-size: 0.75rem; background: #0f766e; color: white; padding: 2px 8px; border-radius: 10px;">${data.source || 'AI Clinical Engine'}</span>
              </div>
              <div style="font-size: 0.92rem;">${formatted}</div>
            </div>
          `;
        } else {
          aiResultBox.innerHTML = `<div class="alert alert-danger">${data.error || 'Failed to process AI diagnosis.'}</div>`;
        }
      })
      .catch(err => {
        aiBtn.disabled = false;
        aiBtn.innerHTML = '<span>✨ AI Clinical Diagnosis</span>';
        aiResultBox.innerHTML = `<div class="alert alert-danger">Error connecting to AI service.</div>`;
      });
    });
  }
});
