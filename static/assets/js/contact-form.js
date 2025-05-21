function submitForm(event) {
    event.preventDefault(); // Prevent the default form submission
    // Get form values
    const fullName = document.getElementById('full_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();

    // Validate form inputs
    if (!fullName || !email || !message) {
        let missingFields = [];
        if (!fullName) missingFields.push('Full Name');
        if (!email) missingFields.push('Email');
        if (!message) missingFields.push('Message');

        alert('Please fill in the following fields: ' + missingFields.join(', '));
        return; // Stop the form submission
    }
    const formData = new FormData(event.target);

    fetch('/send-email', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data); // Debugging line
        if (data.message) {
            alert(data.message);
            // Reset the form fields after the user clicks "OK" on the alert
            document.getElementById('full_name').value = '';
            document.getElementById('email').value = '';
            document.getElementById('message').value = '';
        } else {
            alert('Unexpected error occurred.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to send email.');
    });
}
