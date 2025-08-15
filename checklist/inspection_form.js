document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:3000/api';

    // --- DOM Elements ---
    const quoteNumberEl = document.getElementById('quote-number');
    const customerNameEl = document.getElementById('customer-name');
    const quoteDateEl = document.getElementById('quote-date');
    const inspectorNameInput = document.getElementById('inspector-name');
    const checklistSelect = document.getElementById('checklist-select');
    
    const checklistContainer = document.getElementById('checklist-container');
    const photosContainer = document.getElementById('photos-container');
    const finalizationContainer = document.getElementById('finalization-container');
    const actionsContainer = document.getElementById('actions-container');

    const checklistTbody = document.getElementById('checklist-items-tbody');
    const unitStatusSelect = document.getElementById('unit-status');
    const overallCommentsTextarea = document.getElementById('overall-comments');
    const submitBtn = document.getElementById('submit-inspection-btn');
    const saveDraftBtn = document.getElementById('save-draft-btn');

    // --- State ---
    let currentQuoteId = null;
    let currentChecklistId = null;
    let checklistItems = [];

    // --- API Functions ---
    const api = {
        getChecklists: () => fetch(`${API_BASE_URL}/checklists`).then(res => res.json()),
        getChecklistItems: (id) => fetch(`${API_BASE_URL}/checklists/${id}/items`).then(res => res.json()),
        createInspection: (data) => fetch(`${API_BASE_URL}/inspections`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => res.json()),
        createInspectionResult: (data) => fetch(`${API_BASE_URL}/inspection-results`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
    };

    // --- UI Rendering ---
    const renderChecklistDropdown = (checklists) => {
        checklists.forEach(c => {
            const option = new Option(c.name, c.id);
            checklistSelect.add(option);
        });
    };

    const renderChecklistItems = () => {
        checklistTbody.innerHTML = '';
        if (checklistItems.length === 0) {
            checklistTbody.innerHTML = `<tr><td colspan="3" class="text-center py-4">No items in this checklist.</td></tr>`;
            return;
        }
        checklistItems.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-[var(--border-color)]';
            tr.dataset.itemId = item.id;
            tr.innerHTML = `
                <td class="py-4 pr-4 align-top">
                    <div class="font-medium text-[var(--text-primary)]">${item.item_text}</div>
                    ${item.category ? `<div class="text-xs text-gray-500">${item.category}</div>` : ''}
                </td>
                <td class="py-4 px-4 align-top">
                    <div class="relative">
                        <select class="item-status w-full appearance-none rounded-lg border border-[var(--border-color)] bg-white px-3 py-2 pr-8 text-sm focus:border-[var(--primary-color)] focus:outline-none focus:ring-1 focus:ring-[var(--primary-color)]">
                            <option>Not Checked</option>
                            <option>Passed</option>
                            <option>Failed</option>
                        </select>
                        <span class="material-icons absolute top-1/2 right-2 -translate-y-1/2 pointer-events-none text-gray-400">unfold_more</span>
                    </div>
                </td>
                <td class="py-4 pl-4 align-top">
                    <input class="item-comment w-full rounded-lg border border-[var(--border-color)] px-3 py-2 text-sm focus:border-[var(--primary-color)] focus:outline-none focus:ring-1 focus:ring-[var(--primary-color)]" placeholder="Add a note..." type="text"/>
                </td>
            `;
            checklistTbody.appendChild(tr);
        });
    };
    
    const toggleChecklistVisibility = (visible) => {
        const containers = [checklistContainer, photosContainer, finalizationContainer, actionsContainer];
        containers.forEach(c => c.classList.toggle('hidden', !visible));
    };

    // --- Event Handlers ---
    checklistSelect.addEventListener('change', async () => {
        currentChecklistId = checklistSelect.value ? parseInt(checklistSelect.value, 10) : null;
        if (currentChecklistId) {
            try {
                checklistItems = await api.getChecklistItems(currentChecklistId);
                renderChecklistItems();
                toggleChecklistVisibility(true);
            } catch (error) {
                console.error('Failed to load checklist items:', error);
                alert('Could not load checklist items.');
                toggleChecklistVisibility(false);
            }
        } else {
            checklistItems = [];
            toggleChecklistVisibility(false);
        }
    });

    submitBtn.addEventListener('click', async () => {
        if (!currentQuoteId || !currentChecklistId || !inspectorNameInput.value) {
            alert('Please fill out the inspector name and select a checklist before submitting.');
            return;
        }

        const inspectionData = {
            quote_id: currentQuoteId,
            checklist_id: currentChecklistId,
            inspector_name: inspectorNameInput.value,
            unit_status: unitStatusSelect.value,
            repair_quote_needed: document.querySelector('input[name="repair-quote"]:checked').value === 'true',
            overall_comments: overallCommentsTextarea.value,
            status: 'Submitted'
        };

        try {
            const newInspection = await api.createInspection(inspectionData);
            if (!newInspection.id) {
                throw new Error(newInspection.error || 'Failed to create inspection record.');
            }

            const resultPromises = [];
            const itemRows = checklistTbody.querySelectorAll('tr[data-item-id]');
            itemRows.forEach(row => {
                const resultData = {
                    inspection_id: newInspection.id,
                    checklist_item_id: parseInt(row.dataset.itemId, 10),
                    status: row.querySelector('.item-status').value,
                    comments: row.querySelector('.item-comment').value
                };
                resultPromises.push(api.createInspectionResult(resultData));
            });

            await Promise.all(resultPromises);

            alert('Inspection submitted successfully!');
            window.location.reload(); // Or redirect to a confirmation page

        } catch (error) {
            console.error('Error submitting inspection:', error);
            alert(`An error occurred: ${error.message}`);
        }
    });

    // --- Initialization ---
    const init = async () => {
        // 1. Get Quote ID from URL
        const params = new URLSearchParams(window.location.search);
        currentQuoteId = params.get('quote_id');
        
        if (currentQuoteId) {
            quoteNumberEl.textContent = currentQuoteId;
            // In a real app, you'd fetch quote details here
            customerNameEl.textContent = `Customer for ${currentQuoteId}`;
            quoteDateEl.textContent = new Date().toLocaleDateString();
        } else {
            document.querySelector('.max-w-4xl.mx-auto').innerHTML = 
                '<div class="text-center bg-white p-8 rounded-lg shadow-lg"><h1 class="text-2xl font-bold text-red-600">Error: No Quote ID Provided</h1><p class="mt-2 text-gray-600">Please access this page with a `quote_id` in the URL. Example: .../inspection_form.html?quote_id=QT-12345</p></div>';
            return;
        }

        // 2. Load checklists
        try {
            const checklists = await api.getChecklists();
            renderChecklistDropdown(checklists);
        } catch (error) {
            console.error('Failed to load checklists:', error);
            checklistSelect.innerHTML = '<option>Error loading checklists</option>';
            checklistSelect.disabled = true;
        }
    };

    init();
});