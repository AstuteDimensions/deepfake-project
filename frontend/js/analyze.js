const uploadForm = document.getElementById('uploadForm');

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const resultsCard = document.getElementById('resultsCard');
    const outputStatus = document.getElementById('outputStatus');

    if (fileInput.files.length === 0) {
        alert("Please select an image file first.");
        return;
    }

    await analyzeImage(
        fileInput.files[0],
        resultsCard,
        outputStatus
    );
});


// ==========================================
// ANALYZE IMAGE
// ==========================================

async function analyzeImage(file, resultsCard, outputStatus) {

    const formData = new FormData();

    formData.append('file', file);

    resultsCard.classList.remove('hidden');

    outputStatus.innerText =
        "Analyzing image with AI model...";

    try {

        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {

            outputStatus.innerHTML = `
                <strong>File:</strong> ${data.filename}<br>
                <strong>Status:</strong> ${
                    data.is_fake
                    ? '⚠️ Deepfake Detected'
                    : '✅ Authentic'
                }<br>
                <strong>Confidence:</strong> ${data.confidence}<br>
                <strong>Details:</strong> ${data.details}
            `;

        } else {

            outputStatus.innerText =
                "Error: " +
                (data.error || "Analysis failed.");

        }

    } catch (err) {

        outputStatus.innerText =
            "An error occurred while connecting to the server.";

        console.error(err);
    }
}


// ==========================================
// RECEIVE IMAGE FROM DASHBOARD
// ==========================================

window.addEventListener("load", async () => {

    const storedImage =
        sessionStorage.getItem("selectedImage");

    if (!storedImage) {
        return;
    }

    sessionStorage.removeItem("selectedImage");

    try {

        const response =
            await fetch(storedImage);

        const blob =
            await response.blob();

        const file =
            new File(
                [blob],
                "dashboard_upload.jpg",
                {
                    type: blob.type
                }
            );

        const resultsCard =
            document.getElementById('resultsCard');

        const outputStatus =
            document.getElementById('outputStatus');

        await analyzeImage(
            file,
            resultsCard,
            outputStatus
        );

    } catch (error) {

        console.error(
            "Could not load dashboard image:",
            error
        );

    }

});