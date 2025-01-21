<div class="col-md-12 text-center">
    <div class="button-spinner-row" style="display: inline-flex; align-items: center;">
        <button type="button" id="fetch-data" class="btn btn-primary mx-2">Update Map</button>
        <!-- Spinner wheel -->
        <div id="update-spinner" style="display: none; margin-left: 10px;">
            <img src="static/assets/img/spinner.gif" alt="Loading..." style="width: 20px; height: 20px;">
        </div>
    </div>
</div>
JavaScript
document.addEventListener("DOMContentLoaded", function() {
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }

    document.getElementById('fetch-data').addEventListener('click', function() {
        // Show the loading spinner
        document.getElementById('update-spinner').style.display = 'block';

        updateMap();
    });
});

function updateMap() {
    var form = document.getElementById('mapForm');
    var formData = new FormData(form);
    var settings = {};
    // Include all form elements, including unchecked checkboxes
    Array.from(form.elements).forEach(element => {
        if (element.type === 'checkbox') {
            settings[element.name] = element.checked;
        } else if (element.name) {
            settings[element.name] = element.value;
        }
    });
    fetch('/update_map', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('map').innerHTML = data.map;
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        // Hide the loading spinner
        document.getElementById('update-spinner').style.display = 'none';
    });
}