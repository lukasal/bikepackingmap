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

    // Enable drag-and-drop functionality
    $("#data-table tbody").sortable({
        items: 'tr',
        update: function(event, ui) {
            console.log("Row moved!");
        }
    }).disableSelection();
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

                if (files.length > 50) {
                    alert('You can only upload up to 50 files.');
                    console.log('50 files limit:');
                    resolve('File limit exceeded');
                    return;
                }

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
            sendRequest(formData).then(resolve).catch(error => {
                const errorMessage = error.responseJSON && error.responseJSON.error ? error.responseJSON.error : "An unknown error occurred.";
                showErrorModal(errorMessage);  // Show error message in a popup
                console.error("AJAX error:", error);
                reject(error);
            });
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

                // Check for errors in the response
                if (response.errors && response.errors.length > 0) {
                    const filenames = response.errors.join("\n");
                    const errorMessage = `Error in parsing files:\n${filenames}\nThese files have been excluded.`;
                    console.error("Loading error:", errorMessage);

                    alert(errorMessage);
                }

                response.data.forEach(function(item) {
                    const row = `<tr class="sortable-row">
                                    <td><input type="checkbox" name="selected_activities" class="checkbox-cell" data-id="${item.id}"></td>
                                    <td><input type="datetime-local" class="non-editable" name="start_date[]"  value="${item.start_date}"></td>
                                    <td><input type="text"class="non-editable" name="name[]"  value="${item.name}"></td>
                                    <td><input type="text" class="non-editable" name="type[]"  value="${item.type}"></td>
                                </tr>`;
                    $('#data-table tbody').append(row);
                });
                // Attach event handler for "Select All" checkbox
                $('#select-all').change(function() {
                    $('.checkbox-cell').prop('checked', this.checked);
                });
                resolve();
            },
            error: function(xhr, status, error) {
                if (xhr.status === 401 && xhr.responseJSON && xhr.responseJSON.session_expired) {
                    // Handle session expiration: Redirect user to login page or show message
                    window.location.href = '/session-expired';  // Or use any other redirect mechanism
                } else {
                    // Handle other errors
                    const errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : "An unknown error occurred.";
                    showErrorModal(errorMessage);  // Show error message in a popup
                    console.error("AJAX error:", error);
                    reject(error);
                }
            }
        });
    });
}

// Collect selected checkbox IDs and edited data on form submit
function submitActivities() {
    return new Promise((resolve, reject) => {
        const selectedIds = [];
        const editedData = [];

        // Collect selected checkbox IDs
        console.log('Activities submitted');
        $('.checkbox-cell:checked').each(function() {
            selectedIds.push($(this).data('id'));  // Get the ID from data-id attribute
        });

        // Collect edited data from the table
        $('#data-table tbody tr').each(function() {
            const row = $(this);
            const id = row.find('.checkbox-cell').data('id');
            const date = row.find('input[name="start_date[]"]').val();
            const name = row.find('input[name="name[]"]').val();
            const type = row.find('input[name="type[]"]').val();

            editedData.push({ id, date, name, type });
        });

        // If no checkboxes are selected, alert the user and prevent form submission
        if (selectedIds.length === 0) {
            console.log('No activities submitted');
            alert('Please select at least one activity.');
            reject();
        } else {
            // Optionally, you can handle the selectedIds (e.g., pass them to the server via AJAX)
            console.log('Selected IDs:', selectedIds);
            console.log('Edited Data:', editedData);

            // Clear previously added hidden inputs (in case this is a re-submit)
            $('#activity-form input[name="selected_activities"]').remove();
            $('#activity-form input[name="edited_data"]').remove();

            // Add selected IDs as hidden inputs to the form
            selectedIds.forEach(function(id) {
                $('<input>').attr({
                    type: 'hidden',
                    name: 'selected_activities',  // The same name as the form field
                    value: id  // The value of each selected ID
                }).appendTo('#activity-form');
            });

            // Add edited data as hidden inputs to the form
            $('<input>').attr({
                type: 'hidden',
                name: 'edited_data',
                value: JSON.stringify(editedData)  // Convert edited data to JSON string
            }).appendTo('#activity-form');

            resolve();
        }
    });
}
