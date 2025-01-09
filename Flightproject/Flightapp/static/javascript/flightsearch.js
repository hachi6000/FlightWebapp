// Set minimum date for departure and return dates to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('departure-date').setAttribute('min', today);
    document.getElementById('return-date').setAttribute('min', today);
}

// Call the function when the page loads
window.onload = setMinDate;

const returnInput = document.getElementById('return-date');
const radioButtons = document.querySelectorAll('input[name="flight-type"]');

radioButtons.forEach(radio => {
    radio.addEventListener('change', () => {
        if (radio.value === 'return') {
            returnInput.style.display = 'block';
        } else {
            returnInput.style.display = 'none';
        }
    });
});

if (document.querySelector('input[name="flight-type"]:checked').value === 'one-way') {
    returnInput.style.display = 'none';
} else {
    returnInput.style.display = 'block';
}

// Check if the departure and arrival locations are the same
function validateLocations() {
    const fromSelect = document.getElementById('from');
    const toSelect = document.getElementById('to');

    fromSelect.addEventListener('change', checkSameLocation);
    toSelect.addEventListener('change', checkSameLocation);

    function checkSameLocation() {
        if (fromSelect.value && toSelect.value && fromSelect.value === toSelect.value) {
            alert("Departure and arrival locations cannot be the same. Please select a different destination.");
            toSelect.value = ""; // Reset the destination field
        }
    }
}

// Call the validateLocations function when the page loads
window.onload = function() {
    setMinDate();
    validateLocations();
};




