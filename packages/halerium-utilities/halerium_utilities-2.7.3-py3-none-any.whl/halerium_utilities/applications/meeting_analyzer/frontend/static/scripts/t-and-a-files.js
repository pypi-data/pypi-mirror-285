class TandA {
    constructor() {
        this.btnTranscribeAnalyzeFiles = document.getElementById('btnTranscribeAnalyzeFiles');
        this.divFileNames = document.querySelectorAll('.fileName');

        console.log(this.divFileNames);

        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.btnTranscribeAnalyzeFiles) {
            this.btnTranscribeAnalyzeFiles.addEventListener('click', (event) => {
                event.preventDefault();
                this.btnTranscribeAnalyzeFiles.classList.add("disabled");
                this.sendForTandA();
            });
        }
    }

    async sendForTandA() {
        // get all file names from the divs
        this.divFileNames = document.querySelectorAll('.fileName');
        const fileNames = [];
        for (const divFileName of this.divFileNames) {
            fileNames.push(divFileName.textContent);
        }

        console.log(fileNames);
        console.log(JSON.stringify(fileNames));

        if (!fileNames.length) {
            alert("Please upload and select a file first.");
            return;
        }


        const formData = new FormData();
        formData.append("fileNames", fileNames);

        try {
            const response = await fetch("transcribe_and_analyze_files", {
                method: "POST",
                body: formData
            });

            const data = await response.text();
            document.open();
            document.write(data);
            document.close();
            
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

// Initialize the Selector class when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new TandA();
});
