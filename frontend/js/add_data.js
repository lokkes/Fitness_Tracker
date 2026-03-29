document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('photo-dropzone');
    const fileInput = document.getElementById('photo-upload');
    const preview = document.getElementById('photo-preview');

    if (!dropzone || !fileInput || !preview) {
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
});
