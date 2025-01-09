function validateLetters(input) {
    input.value = input.value.replace(/[^A-Za-z]/g, ''); // Allow only A-Z or a-z characters
}

function validatePhone(input) {
    input.value = input.value.replace(/[^0-9]/g, ''); // Allow only digits
}

function validateForm() {
    // Add any additional form validation if needed
    const firstName = document.getElementById("first-name").value;
    const lastName = document.getElementById("last-name").value;
    const phone = document.getElementById("signup-phone").value;

    if (!firstName || !lastName || !phone) {
        alert("Please fill in all required fields.");
        return false;
    }

    return true; // Proceed with form submission
}
