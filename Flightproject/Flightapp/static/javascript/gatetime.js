
function updateClock() {
    // Create a new Date object
    const now = new Date();
    
    // Get current time components
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();

    // Format minutes and seconds to always have two digits
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = seconds < 10 ? '0' + seconds : seconds;

    // Determine AM/PM
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12; // Convert 24-hour format to 12-hour format
    hours = hours ? hours : 12; // Handle 12 PM as 12, not 0
    const timeString = `${hours}:${minutes}:${seconds}`;

    // Get current date components
    const day = now.getDate();
    const month = now.getMonth() + 1; // Months are zero-indexed (0 = January)
    const year = now.getFullYear();
    const dateString = `${month}/${day}/${year}`;

    // Update the DOM
    document.getElementById('time').textContent = timeString;
    document.getElementById('ampm').textContent = ampm;
    document.getElementById('date').textContent = dateString;
}

// Update the clock every second
setInterval(updateClock, 1000);

// Call the update function immediately to avoid delay
updateClock();
