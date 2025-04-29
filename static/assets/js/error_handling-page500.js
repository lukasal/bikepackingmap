document.getElementById('notify-form-page500').addEventListener('submit', function(e) {
    e.preventDefault(); // Stop the form from submitting normally
  
    const form = e.target;
    const emailInput = document.getElementById('email');
    const submitButton = document.getElementById('submit-button');
  
    const email = emailInput.value.trim();
    if (!email) {
      alert("Please enter a valid email.");
      return;
    }
  
    submitButton.textContent = "Submitting...";
    submitButton.disabled = true;
  
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
      return response.json();
    })
    .then(data => {
      if (data && data.message) {
        // alert(data.message);
      } else {
        alert('Unexpected response from server.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred. Please try again later.');
    })
    .finally(() => {
      form.innerHTML = "<div class='text-center mt-4'><p>Thank you very much! We will reach out to you.</p></div>";
    });
  });