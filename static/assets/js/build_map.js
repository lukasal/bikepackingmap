$(document).ready(function() {
    $('.collapsible').click(function() {
        $(this).toggleClass('active');
        var content = $(this).next();
        content.toggle();
    });
});

function updateMap() {
    return new Promise((resolve, reject) => {
        var form = $('#mapForm')[0];
        var settings = {};
        // Include all form elements, including unchecked checkboxes
        $.each(form.elements, function(index, element) {
            if (element.type === 'checkbox') {
                settings[element.name] = element.checked;
            } else if (element.name) {
                settings[element.name] = element.value;
            }
        });
        $.ajax({
            url: '/update_map',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(settings),
            success: function(data) {
                $('#map').html(data.map);
                resolve();
            },
            error: function(error) {
                console.error('Error:', error);
                reject(error);
            }
        });
    });
}