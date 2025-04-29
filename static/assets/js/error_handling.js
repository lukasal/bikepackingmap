// Load the modal HTML dynamically into the page (first time only)
function loadErrorModal() {
    fetch('templates/includes/error.html')
        .then(response => response.text())
        .then(html => {
            document.body.insertAdjacentHTML('beforeend', html);
        })
        .catch(err => console.error('Error loading error modal:', err));
}

// Function to display the error modal with a message
function showErrorModal() {
    document.getElementById("error-modal").style.display = "block";
}

function closeErrorModal() {
    document.getElementById("error-modal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("notify-form");
    const submitButton = form.querySelector("button"); // Assuming a submit button exists
    const closeButton = document.getElementById("close-modal"); // Close button

    // Handle form submission
    form.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent default form submission
        const email = form.email.value; // Get the email value

        // Disable the submit button to prevent multiple clicks
        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        // Send the email to the server
        fetch("/notify", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `email=${encodeURIComponent(email)}`
        })
        .then(data => {
            console.log('Response data:', data); // Debugging line
            if (data.message) {
                alert(data.message);
                // Reset the form fields after the user clicks "OK" on the alert
                document.getElementById('email').value = '';
            } else {
                alert('Unexpected error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to send email.');
        });;
    });

    // Handle close button click to trigger closeErrorModal function
    if (closeButton) {
        closeButton.addEventListener("click", closeErrorModal);
    }
});