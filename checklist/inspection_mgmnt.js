document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:3000/api';
    
    // State
    let checklistsCache = [];
    let itemsCache = [];
    let currentChecklistId = null;

    // Checklist UI Elements
    const checklistSelect = document.getElementById('checklist-select');
    const newChecklistBtn = document.getElementById('new-checklist-btn');
    const renameChecklistBtn = document.getElementById('rename-checklist-btn');
    const deleteChecklistBtn = document.getElementById('delete-checklist-btn');
    const mainTitle = document.getElementById('main-title');
    const mainDescription = document.getElementById('main-description');

    // Items UI Elements
    const itemsContainer = document.getElementById('items-container');
    const tbody = document.getElementById('checklist-tbody');
    const addItemBtn = document.getElementById('add-item-btn');
    
    // Modal UI Elements
    const modal = document.getElementById('item-modal');
    const modalTitle = document.getElementById('modal-title');
    const cancelBtn = document.getElementById('cancel-btn');
    const saveBtn = document.getElementById('save-item-btn');
    const form = document.getElementById('item-form');
    const itemIdInput = document.getElementById('item-id');
    const itemTextInput = document.getElementById('item-text');
    const itemCategoryInput = document.getElementById('item-category');
    const itemRequiredInput = document.getElementById('item-required');

    // --- API Functions ---
    const api = {
        getChecklists: () => fetch(`${API_BASE_URL}/checklists`).then(res => res.json()),
        createChecklist: (name) => fetch(`${API_BASE_URL}/checklists`, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ name })
        }).then(res => res.json()),
        renameChecklist: (id, name) => fetch(`${API_BASE_URL}/checklists/${id}`, {
            method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ name })
        }),
        deleteChecklist: (id) => fetch(`${API_BASE_URL}/checklists/${id}`, { method: 'DELETE' }),
        
        getItems: (checklistId) => fetch(`${API_BASE_URL}/checklists/${checklistId}/items`).then(res => res.json()),
        createItem: (checklistId, data) => fetch(`${API_BASE_URL}/checklists/${checklistId}/items`, {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
        }),
        updateItem: (itemId, data) => fetch(`${API_BASE_URL}/checklist-items/${itemId}`, {
            method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
        }),
        deleteItem: (itemId) => fetch(`${API_BASE_URL}/checklist-items/${itemId}`, { method: 'DELETE' })
    };

    // --- UI Update Functions ---
    const updateChecklistDropdown = () => {
        checklistSelect.innerHTML = '<option value="">-- Select a Checklist --</option>';
        checklistsCache.forEach(c => {
            const option = new Option(c.name, c.id);
            checklistSelect.add(option);
        });
        checklistSelect.value = currentChecklistId;
    };

    const updateUIForSelection = () => {
        const isChecklistSelected = !!currentChecklistId;
        renameChecklistBtn.disabled = !isChecklistSelected;
        deleteChecklistBtn.disabled = !isChecklistSelected;
        itemsContainer.classList.toggle('hidden', !isChecklistSelected);

        if (isChecklistSelected) {
            const selected = checklistsCache.find(c => c.id == currentChecklistId);
            mainTitle.textContent = selected.name;
            mainDescription.textContent = `Manage the items for the "${selected.name}" checklist.`;
        } else {
            mainTitle.textContent = 'Inspection Checklists';
            mainDescription.textContent = 'Select a checklist to view or edit its items, or create a new one.';
        }
    };

    const renderItemsTable = () => {
        tbody.innerHTML = '';
        if (itemsCache.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4">No items in this checklist. Click "Add New Item" to get started.</td></tr>`;
            return;
        }
        itemsCache.forEach((item) => {
            const tr = document.createElement('tr');
            tr.className = 'bg-white border-b hover:bg-gray-50';
            tr.dataset.id = item.id;
            tr.innerHTML = `
                <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">${item.item_text}</td>
                <td class="px-6 py-4"><span class="bg-blue-100 text-blue-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full">${item.category || 'N/A'}</span></td>
                <td class="px-6 py-4 text-center">
                    <input type="checkbox" class="h-5 w-5 rounded border-gray-300" ${item.is_required ? 'checked' : ''} disabled>
                </td>
                <td class="px-6 py-4 text-right flex items-center justify-end gap-2">
                    <button class="p-2 rounded-full hover:bg-gray-200 transition-colors edit-btn" data-id="${item.id}"><span class="material-icons text-gray-600 pointer-events-none">edit</span></button>
                    <button class="p-2 rounded-full hover:bg-red-100 transition-colors delete-btn" data-id="${item.id}"><span class="material-icons text-red-500 pointer-events-none">delete</span></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    };

    // --- Main Logic Functions ---
    const loadChecklists = async () => {
        try {
            checklistsCache = await api.getChecklists();
            updateChecklistDropdown();
            // If there was a selection, try to maintain it. Otherwise, select nothing.
            const selectedExists = checklistsCache.some(c => c.id == currentChecklistId);
            if (!selectedExists) {
                currentChecklistId = null;
            }
            updateUIForSelection();
        } catch (error) {
            console.error('Failed to load checklists:', error);
            alert('Could not load checklists. Is the API server running?');
        }
    };

    const handleChecklistSelection = async (id) => {
        currentChecklistId = id ? parseInt(id, 10) : null;
        updateUIForSelection();
        if (currentChecklistId) {
            try {
                itemsCache = await api.getItems(currentChecklistId);
                renderItemsTable();
            } catch (error) {
                console.error(`Failed to load items for checklist ${currentChecklistId}:`, error);
                tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4">Error loading items.</td></tr>`;
            }
        } else {
            itemsCache = [];
            renderItemsTable();
        }
    };

    // --- Event Handlers ---
    checklistSelect.addEventListener('change', () => handleChecklistSelection(checklistSelect.value));

    newChecklistBtn.addEventListener('click', async () => {
        const name = prompt('Enter the name for the new checklist:');
        if (name) {
            try {
                const newChecklist = await api.createChecklist(name);
                if (newChecklist.id) {
                    currentChecklistId = newChecklist.id;
                    await loadChecklists();
                    handleChecklistSelection(currentChecklistId);
                } else {
                    alert(`Error: ${newChecklist.error || 'Could not create checklist.'}`);
                }
            } catch (error) {
                console.error('Error creating checklist:', error);
                alert('Failed to create checklist.');
            }
        }
    });

    renameChecklistBtn.addEventListener('click', async () => {
        if (!currentChecklistId) return;
        const selected = checklistsCache.find(c => c.id == currentChecklistId);
        const newName = prompt('Enter the new name for the checklist:', selected.name);
        if (newName && newName !== selected.name) {
            try {
                await api.renameChecklist(currentChecklistId, newName);
                await loadChecklists();
            } catch (error) {
                console.error('Error renaming checklist:', error);
                alert('Failed to rename checklist.');
            }
        }
    });

    deleteChecklistBtn.addEventListener('click', async () => {
        if (!currentChecklistId) return;
        const selected = checklistsCache.find(c => c.id == currentChecklistId);
        if (confirm(`Are you sure you want to delete the "${selected.name}" checklist and all its items? This cannot be undone.`)) {
            try {
                await api.deleteChecklist(currentChecklistId);
                currentChecklistId = null;
                await loadChecklists();
                handleChecklistSelection(null);
            } catch (error) {
                console.error('Error deleting checklist:', error);
                alert('Failed to delete checklist.');
            }
        }
    });

    // --- Item Modal Logic ---
    const openModal = (item = null) => {
        form.reset();
        if (item) {
            modalTitle.textContent = 'Edit Checklist Item';
            itemIdInput.value = item.id;
            itemTextInput.value = item.item_text;
            itemCategoryInput.value = item.category;
            itemRequiredInput.checked = item.is_required;
        } else {
            modalTitle.textContent = 'Add New Checklist Item';
            itemIdInput.value = '';
        }
        modal.classList.remove('hidden');
    };

    const closeModal = () => modal.classList.add('hidden');

    const handleItemFormSubmit = async () => {
        if (!currentChecklistId) return;
        const id = itemIdInput.value ? parseInt(itemIdInput.value, 10) : null;
        const itemData = {
            item_text: itemTextInput.value,
            category: itemCategoryInput.value,
            is_required: itemRequiredInput.checked,
            display_order: id ? itemsCache.find(i => i.id == id).display_order : itemsCache.length + 1
        };

        try {
            const promise = id ? api.updateItem(id, itemData) : api.createItem(currentChecklistId, itemData);
            const response = await promise;
            if (!response.ok) throw new Error(await response.text());
            closeModal();
            handleChecklistSelection(currentChecklistId); // Refresh table
        } catch (error) {
            console.error('Error saving item:', error);
            alert('Could not save the item.');
        }
    };

    const handleItemDelete = async (id) => {
        if (!confirm('Are you sure you want to delete this item?')) return;
        try {
            await api.deleteItem(id);
            handleChecklistSelection(currentChecklistId); // Refresh table
        } catch (error) {
            console.error('Error deleting item:', error);
            alert('Could not delete the item.');
        }
    };

    addItemBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    saveBtn.addEventListener('click', handleItemFormSubmit);
    tbody.addEventListener('click', (e) => {
        const editBtn = e.target.closest('.edit-btn');
        const deleteBtn = e.target.closest('.delete-btn');
        if (editBtn) {
            const id = editBtn.dataset.id;
            const item = itemsCache.find(i => i.id == id);
            openModal(item);
        } else if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            handleItemDelete(id);
        }
    });

    // Initial Load
    loadChecklists();
});