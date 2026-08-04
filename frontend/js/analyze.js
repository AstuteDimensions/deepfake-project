document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevents the default page reload

    const fileInput = document.getElementById('fileInput');
    const resultsCard = document.getElementById('resultsCard');
    const outputStatus = document.getElementById('outputStatus');

    if (fileInput.files.length === 0) {
        alert("Please select an image file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Show loading state
    resultsCard.classList.remove('hidden');
    outputStatus.innerText = "Analyzing image with AI model...";

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            outputStatus.innerHTML = `
                <strong>File:</strong> ${data.filename}<br>
                <strong>Status:</strong> ${data.is_deepfake ? '⚠️ Deepfake Detected' : '✅ Authentic'}<br>
                <strong>Confidence:</strong> ${data.confidence}<br>
                <strong>Details:</strong> ${data.details}
            `;
        } else {
            outputStatus.innerText = "Error: " + (data.error || "Analysis failed.");
        }
    } catch (err) {
        outputStatus.innerText = "An error occurred while connecting to the server.";
        console.error(err);
    }
});