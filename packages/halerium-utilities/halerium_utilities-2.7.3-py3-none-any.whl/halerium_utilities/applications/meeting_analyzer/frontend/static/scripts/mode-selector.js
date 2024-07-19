class Selector {
    constructor() {
        this.btnUploadFile = document.getElementById('btnUploadFile');
        this.btnRecordMeeting = document.getElementById('btnRecordMeeting');
        this.fileInput = document.querySelector('input[type="file"][name="fileInput"]');
        this.uploadForm = document.getElementById('uploadForm');
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.btnUploadFile) {
            this.btnUploadFile.addEventListener('click', (event) => {
                event.preventDefault();
                this.fileInput.click();
            });
        }

        if (this.fileInput) {
            this.fileInput.addEventListener('change', () => {
                if (this.fileInput.files.length > 0) {
                    this.uploadFiles();
                }
            });
        }
    }

    async uploadFiles() {
        const files = this.fileInput.files;
        if (!files.length) {
            alert("Please select at least one file first.");
            return;
        }

        const formData = new FormData();
    
        for (const file of files) {
            formData.append("fileInputs", file);
        }

        try {
            this.btnRecordMeeting.disabled = true;
            this.btnUploadFile.disabled = true;
            this.btnUploadFile.textContent = "Uploading...";
            this.btnUploadFile.style.backgroundColor = "#ccc";
            this.btnRecordMeeting.style.backgroundColor = "#ccc";
            this.btnUploadFile.style.borderColor = "#ccc";
            this.btnRecordMeeting.style.borderColor = "#ccc";

            const response = await fetch(this.uploadForm.action, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.text();
            document.open();
            document.write(data);
            document.close();
        } catch (error) {
            console.error('Error:', error);
        } finally {
            // here we could reset all the buttons.
        }
    }
}

// Initialize the Selector class when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new Selector();
});
