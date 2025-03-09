async function uploadDocument() {
    let fileInput = document.getElementById("fileInput");
    let formData = new FormData();
    formData.append("document", fileInput.files[0]);

    let response = await fetch("/scan", {
        method: "POST",
        body: formData
    });

    let data = await response.json();
    alert(data.message || data.error);
}
