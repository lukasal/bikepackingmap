$(document).ready(function() {
    // Helper function to format the date as YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Set the default dates
    window.onload = function() {
        const endDate = new Date();  // Current date
        const startDate = new Date(); // Default start date (1 month before current date)
        startDate.setMonth(endDate.getMonth() - 1);

        document.getElementById('start_date').value = formatDate(startDate);
        document.getElementById('end_date').value = formatDate(endDate);
    };
});

function fetchData() {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        const startDate = $('#start_date').val();
        const endDate = $('#end_date').val();
        const perPage = $('#per_page').val();

        formData.append('start_date', startDate);
        formData.append('end_date', endDate);
        formData.append('per_page', perPage);

        if (showUploadButton) {
            // Handle file upload
            const fileInput = $('<input type="file" multiple>').on('change', function(event) {
                const files = event.target.files;
                for (let i = 0; i < files.length; i++) {
                    formData.append('gpx_files', files[i]);
                }
                    
                // Send AJAX request to upload files
                sendRequest(formData).then(resolve).catch(reject);
            });

            // Trigger the file input click to open the file explorer
            fileInput.click();
        } else {
            // Send AJAX request to fetch data
            sendRequest(formData).then(resolve).catch(reject);
        }
    });
}

function sendRequest(formData) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: fetchUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log(response);  // Log the entire response
                $('#data-table tbody').empty(); // Clear existing data
                response.data.forEach(function(item) {
                    const row = `<tr>
                                    <td><input type="checkbox" name="selected_activities" class="select-row" data-id="${item.id}"></td>
                                    <td>${item.start_date}</td>
                                    <td>${item.name}</td>
                                    <td>${item.type}</td>
                                </tr>`;
                    $('#data-table tbody').append(row);
                });
                // Attach event handler for "Select All" checkbox
                $('#select-all').change(function() {
                    $('.select-row').prop('checked', this.checked);
                });
                resolve();
            },
            error: function(xhr, status, error) {
                if (xhr.status === 401 && xhr.responseJSON && xhr.responseJSON.session_expired) {
                    // Handle session expiration: Redirect user to login page or show message
                    window.location.href = '/session-expired';  // Or use any other redirect mechanism
                } else {
                    // Handle other errors
                    console.error("AJAX error:", error);
                    reject(error);
                }
            }
        });
    });
}

// Collect selected checkbox IDs on form submit
function submitActivities() {
    return new Promise((resolve, reject) => {
        const selectedIds = [];
        // Collect selected checkbox IDs
        console.log('Activities submitted')
        $('.select-row:checked').each(function() {
            selectedIds.push($(this).data('id'));  // Get the ID from data-id attribute
        });
        
        // If no checkboxes are selected, alert the user and prevent form submission
        if (selectedIds.length === 0) {
            console.log('No activities submitted')
            alert('Please select at least one activity.');
            resolve();
        } else {
            // Optionally, you can handle the selectedIds (e.g., pass them to the server via AJAX)
            console.log('Selected IDs:', selectedIds);
            // Clear previously added hidden inputs (in case this is a re-submit)
            $('#activity-form input[name="selected_activities"]').remove();
            // Add selected IDs as hidden inputs to the form    
            selectedIds.forEach(function(id) {
                $('<input>').attr({
                    type: 'hidden',
                    name: 'selected_activities',  // The same name as the form field
                    value: id  // The value of each selected ID
                }).appendTo('#activity-form');
            });
            resolve();
        }
    });
}