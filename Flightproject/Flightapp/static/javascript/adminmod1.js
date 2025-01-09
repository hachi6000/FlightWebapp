// Existing JavaScript code

const oneWayRadio = document.getElementById('one-way');
const returnRadio = document.getElementById('return');
const returnDateContainer = document.getElementById('return-date-container');
const departureDateInput = document.getElementById('departure-date'); // Assuming the departure date input has this ID
const returnDateInput = document.getElementById('return-date'); // Assuming the return date input has this ID

// Function to set minimum date for departure date as today's date
function setMinDepartureDate() {
    const today = new Date().toISOString().split('T')[0]; // Get today's date in YYYY-MM-DD format
    departureDateInput.min = today; // Set the minimum date for the departure date
}

// Function to show/hide return date and return time based on selected flight type
function toggleReturnDate() {
    if (returnRadio.checked) {
        returnDateContainer.style.display = 'block';
    } else {
        returnDateContainer.style.display = 'none';
    }
}

// Function to validate that the return date is later than the departure date
function validateReturnDate() {
    const departureDate = new Date(departureDateInput.value);
    const returnDate = new Date(returnDateInput.value);

    // Check if return date is earlier than or equal to departure date
    if (returnDate <= departureDate) {
        alert('Return date must be later than the departure date.');
        returnDateInput.value = ''; // Clear the return date if invalid
        returnDateInput.setCustomValidity('Return date must be later than departure date.');
    } else {
        returnDateInput.setCustomValidity(''); // Clear custom validity if the date is valid
    }
}

// Function to ensure return date cannot be earlier than departure date
function updateReturnDateMin() {
    const departureDate = new Date(departureDateInput.value);
    if (departureDateInput.value) {
        // Set minimum return date to be one day after the departure date
        departureDate.setDate(departureDate.getDate() + 1);
        returnDateInput.min = departureDate.toISOString().split('T')[0]; // Set the minimum return date dynamically
    }
}

// Event listeners for the radio buttons
oneWayRadio.addEventListener('change', toggleReturnDate);
returnRadio.addEventListener('change', toggleReturnDate);

// Event listener for the return date input to validate when it's changed
returnDateInput.addEventListener('change', validateReturnDate);

// Event listener to ensure return date is later than the departure date whenever the departure date changes
departureDateInput.addEventListener('change', updateReturnDateMin);

// Initialize the return date and return time visibility on page load
toggleReturnDate();

// Set the minimum departure date to today
setMinDepartureDate();

// Update minimum return date to be one day after departure date if already selected
updateReturnDateMin();

// New validation code for departure and arrival cities

const fromSelect = document.getElementById('from');
const toSelect = document.getElementById('to');
const form = document.querySelector('form');

// Function to validate that departure and arrival cities are not the same
function validateDifferentCities() {
    if (fromSelect.value && fromSelect.value === toSelect.value) {
        alert('Departure and Arrival cities cannot be the same.');
        toSelect.value = ''; // Reset the arrival city selection if invalid
        return false;
    }
    return true;
}

// Add event listeners to validate on selection change
fromSelect.addEventListener('change', validateDifferentCities);
toSelect.addEventListener('change', validateDifferentCities);

// Add a final validation before form submission
form.addEventListener('submit', (event) => {
    if (!validateDifferentCities()) {
        event.preventDefault(); // Prevent form submission if cities are the same
    }
});
