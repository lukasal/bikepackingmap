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
    .catch(error => console.error('Error:', error));
  }