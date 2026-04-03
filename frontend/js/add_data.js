document.addEventListener('DOMContentLoaded', () => {
    console.log('add_data.js loaded');

    const dropzone = document.getElementById('photo-dropzone');
    const fileInput = document.getElementById('photo-upload');
    const preview = document.getElementById('photo-preview');
    const dataForm = document.getElementById('add-dataForm');

    if (!dropzone || !fileInput || !preview || !dataForm) {
        return;
    }

    const showPreview = (file) => {
        if (!file || !file.type.startsWith('image/')) {
            alert('Please choose an image file.');
            return;
        }

        preview.src = URL.createObjectURL(file);
        preview.classList.remove('hidden');
    };

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        showPreview(file);
    });

    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    dropzone.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            fileInput.click();
        }
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (event) => {
        const file = event.dataTransfer.files[0];
        if (!file) {
            return;
        }

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        showPreview(file);
    });

    dataForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log('add-data form submit triggered');

        const email = localStorage.getItem('email');
        if (!email) {
            alert('User not logged in');
            return;
        }

        const formData = new FormData();
        formData.append('email', email);
        formData.append('name', document.getElementById('name').value);
        formData.append('height', document.getElementById('height').value);
        formData.append('weight', document.getElementById('weight').value);
        formData.append('fights', document.getElementById('fights').value);
        formData.append('wins', document.getElementById('wins').value);
        formData.append('losses', document.getElementById('losses').value);
        formData.append('draws', document.getElementById('draws').value);

        const file = fileInput.files[0];
        if (file) {
            formData.append('image', file);
        }

        try {
            console.log('sending POST /add_info');
            const createResponse = await fetch('/add_info', {
                method: 'POST',
                body: formData
            });
            const createData = await createResponse.json();
            console.log('POST /add_info response:', createData);

            if (createData.success) {
                alert('User info created');
                return;
            }

            if (!createData.message || !createData.message.includes('already exists')) {
                alert(createData.message || 'Could not save user info');
                return;
            }

            console.log('sending PUT /add_info');
            const updateResponse = await fetch('/add_info', {
                method: 'PUT',
                body: formData
            });
            const updateData = await updateResponse.json();
            console.log('PUT /add_info response:', updateData);

            if (updateData.success) {
                alert('User info updated successfully!');
                return;
            }

            alert(updateData.message || 'Could not update user info');
        } catch (error) {
            console.error('Add/update user info error:', error);
            alert('Something went wrong while saving user info.');
        }
    });
});
