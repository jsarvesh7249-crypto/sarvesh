document.getElementById('myButton').addEventListener('click', function () {
    // Hide the button
    this.style.display = 'none';

    // Show the message
    document.getElementById('message').classList.remove('hidden');
});
