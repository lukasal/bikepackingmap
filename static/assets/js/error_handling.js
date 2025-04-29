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
        fetch("/notify-on-fix", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `email=${encodeURIComponent(email)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse JSON from the response
        })
        .then(data => {
            console.log('Response data:', data); // Debugging line
            if (data.message) {
                alert(data.message);
                // Reset the form fields after the user clicks "OK" on the alert
                document.getElementById('email').value = '';
                submitButton.textContent = "Notify Me";
                submitButton.disabled = false;

            } else {
                alert('Unexpected error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to send email.');
        })
        .finally(() => {
            document.getElementById('email').value = '';
            submitButton.textContent = "Notify Me";
            submitButton.disabled = false;
            closeErrorModal();
        });
    });

    // Handle close button click to trigger closeErrorModal function
    if (closeButton) {
        closeButton.addEventListener("click", closeErrorModal);
    }
});