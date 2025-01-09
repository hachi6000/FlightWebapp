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
    }
}

async function loadCities(provinceName) {
    try {
        const response = await fetch("{% static 'json/ph_locations.json' %}");
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
    }
}

document.addEventListener('DOMContentLoaded', loadProvinces);
document.getElementById('billing-province').addEventListener('change', function () {
    loadCities(this.value);
});