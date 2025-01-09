    // Enhanced validation for Cardholder's Name and Street
    function validateText(input, minLength) {
        const value = input.value.trim();
        const isValid = value.length >= minLength && /[A-Za-z]/.test(value) && !/^\d+$/.test(value);
        
        if (!isValid) {
            input.setCustomValidity(`Please enter at least ${minLength} characters, with at least one letter, and no all-numeric values.`);
        } else {
            input.setCustomValidity('');
        }
    }

    // Attach validation dynamically
    // Prevent numbers in Cardholder's Name
    document.getElementById('card-name').addEventListener('input', function () {
        this.value = this.value.replace(/[^A-Za-z\s]/g, ''); // Allows only letters and spaces
    });
    function validateCardName(input) {
        // Remove any characters that are not letters or spaces
        input.value = input.value.replace(/[^A-Za-z\s]/g, '');
    }

    document.getElementById('Street').addEventListener('input', function () {
        validateText(this, 5);
    });

    // Input validation for credit card and CVV
    document.getElementById('card-number').addEventListener('input', function () {
        this.value = this.value.replace(/\D/g, '');
    });

    document.getElementById('cvv').addEventListener('input', function () {
        this.value = this.value.replace(/\D/g, '').slice(0, 3);
    });

    // Fetch Provinces and Cities
    async function loadProvinces() {
        try {
            const response = await fetch("{% static 'json/ph_locations.json' %}");
            if (!response.ok) throw new Error(`Failed to fetch provinces: ${response.status}`);
            const data = await response.json();
            const provinceSelect = document.getElementById('billing-province');
            data.provinces.forEach(province => {
                const option = document.createElement('option');
                option.value = province.name;
                option.textContent = province.name;
                provinceSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading provinces:", error);
            alert("Failed to load provinces. Please try again later.");
        }
    }

    async function loadCities(provinceName) {
        try {
            const response = await fetch("{% static 'json/ph_locations.json' %}");
            if (!response.ok) throw new Error(`Failed to fetch cities: ${response.status}`);
            const data = await response.json();
            const citySelect = document.getElementById('billing-city');
            citySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
            const selectedProvince = data.provinces.find(p => p.name === provinceName);
            if (selectedProvince) {
                selectedProvince.cities.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    citySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Error loading cities:", error);
            alert("Failed to load cities. Please try again later.");
        }
    }

    document.addEventListener('DOMContentLoaded', loadProvinces);
    document.getElementById('billing-province').addEventListener('change', function () {
        const selectedProvince = this.value;
        loadCities(selectedProvince);
    });

    // Booking form submission with success message
    document.getElementById('booking-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const successMessage = document.getElementById('success-message');
        successMessage.style.display = 'block';
        setTimeout(() => window.location.href = '/front', 3000);
    });
