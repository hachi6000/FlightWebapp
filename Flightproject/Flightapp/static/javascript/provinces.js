const provinceSelect = document.getElementById('billing-province');
const citySelect = document.getElementById('billing-city');

async function loadProvincesData() {
    try {
        // Retrieve JSON URL from the data attribute in the HTML
        const jsonUrl = document.body.getAttribute('data-json-url');
        console.log("Fetching JSON from:", jsonUrl);

        const response = await fetch(jsonUrl);

        if (!response.ok) {
            console.error('Failed to load JSON:', response.status, response.statusText);
            return;
        }

        const data = await response.json();
        console.log("JSON Data Loaded:", data);

        // Populate the province dropdown
        data.provinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province.name;
            option.textContent = province.name;
            provinceSelect.appendChild(option);
        });

        // Event listener for province selection
        provinceSelect.addEventListener('change', () => {
            const selectedProvince = provinceSelect.value;
            populateCities(selectedProvince, data.provinces);
        });
    } catch (error) {
        console.error('Error fetching JSON data:', error);
    }
}

function populateCities(provinceName, provinces) {
    citySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
    const selectedProvince = provinces.find(province => province.name === provinceName);

    if (selectedProvince) {
        selectedProvince.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    } else {
        console.error('Province not found:', provinceName);
    }
}

document.addEventListener('DOMContentLoaded', loadProvincesData);
