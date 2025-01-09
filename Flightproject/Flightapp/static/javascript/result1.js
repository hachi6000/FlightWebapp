function updatePrice(flightId) {
    const seatClass = document.getElementById(`seatClass${flightId}`).value;
    const priceElement = document.getElementById(`price${flightId}`);
    const basePrice = parseFloat(priceElement.getAttribute('data-base-price'));

    let newPrice = basePrice;

    // Calculate the new price based on the selected seat class
    if (seatClass === 'premium economy') {
        newPrice = basePrice * 1.3; // 30% increase for Premium Economy
    } else if (seatClass === 'business') {
        newPrice = basePrice * 2; // Double the price for Business Class
    }

    // Update the price display
    priceElement.textContent = `${newPrice.toFixed(2)} PHP`;
}
