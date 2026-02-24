// Particles.js Configuration
particlesJS('particles-js', {
    particles: {
        number: {
            value: 80,
            density: {
                enable: true,
                value_area: 800
            }
        },
        color: {
            value: '#ffffff'
        },
        shape: {
            type: 'circle',
        },
        opacity: {
            value: 0.5,
            random: false,
        },
        size: {
            value: 3,
            random: true,
        },
        line_linked: {
            enable: true,
            distance: 150,
            color: '#ffffff',
            opacity: 0.4,
            width: 1
        },
        move: {
            enable: true,
            speed: 2,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false,
        }
    },
    interactivity: {
        detect_on: 'canvas',
        events: {
            onhover: {
                enable: true,
                mode: 'repulse'
            },
            onclick: {
                enable: true,
                mode: 'push'
            },
            resize: true
        },
    },
    retina_detect: true
});

// Global Variables
let selectedEmotion = null;

// Screen Navigation Functions
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
    playClickSound();
}

function showWarning() {
    showScreen('warningScreen');
}

function showPhoneInput() {
    if (!selectedEmotion) {
        alert('Please select how you\'re feeling first!');
        return;
    }
    showScreen('phoneScreen');
}

function goBack() {
    showScreen('welcomeScreen');
    selectedEmotion = null;
    document.querySelectorAll('.emotion-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    const continueBtn = document.getElementById('continueBtn');
    if (continueBtn) continueBtn.disabled = true;
}

// Emotion Selection
function selectEmotion(button) {
    // Remove selection from all buttons
    document.querySelectorAll('.emotion-btn').forEach(btn => {
        btn.classList.remove('selected');
    });

    // Add selection to clicked button
    button.classList.add('selected');
    selectedEmotion = button.dataset.emotion;

    // Enable continue button
    document.getElementById('continueBtn').disabled = false;

    playClickSound();
}

// Phone Validation
function validatePhone() {
    const phoneInput = document.getElementById('phoneNumber');
    const chatBtn = document.getElementById('chatBtn');
    const phoneNumber = phoneInput.value.replace(/\D/g, ''); // Remove non-digits

    phoneInput.value = phoneNumber; // Update input with cleaned value

    // Enable button if phone number is valid (at least 10 digits)
    if (phoneNumber.length >= 10) {
        chatBtn.disabled = false;
    } else {
        chatBtn.disabled = true;
    }
}

// Message Character Count
document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('messageText');
    const charCount = document.getElementById('charCount');

    if (messageInput && charCount) {
        messageInput.addEventListener('input', function () {
            charCount.textContent = String(this.value.length);
        });
    }
});

// Open WhatsApp
function openWhatsApp() {
    const countryCode = document.getElementById('countryCode').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    const message = document.getElementById('messageText').value;

    if (phoneNumber.length < 10) {
        alert('Please enter a valid phone number!');
        return;
    }

    // Show loading screen
    showScreen('loadingScreen');

    // Construct WhatsApp number (remove + from country code, combine with number)
    const fullNumber = countryCode.replace('+', '') + phoneNumber;

    // Encode message for URL
    const encodedMessage = encodeURIComponent(message || '');

    // Construct WhatsApp URL
    let whatsappURL;

    // Check if mobile or desktop
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    if (isMobile) {
        // Mobile WhatsApp app
        whatsappURL = `whatsapp://send?phone=${fullNumber}&text=${encodedMessage}`;
    } else {
        // WhatsApp Web
        whatsappURL = `https://web.whatsapp.com/send?phone=${fullNumber}&text=${encodedMessage}`;
    }

    // Delay before opening WhatsApp
    setTimeout(() => {
        window.open(whatsappURL, '_blank');

        // Show success message and reset after 3 seconds
        setTimeout(() => {
            alert('WhatsApp opened! Good luck with your conversation! 💬');
            resetApp();
        }, 2000);
    }, 1500);
}

// Reset Application
function resetApp() {
    showScreen('welcomeScreen');
    document.getElementById('phoneNumber').value = '';
    document.getElementById('messageText').value = '';
    document.getElementById('charCount').textContent = '0';
    selectedEmotion = null;
    document.querySelectorAll('.emotion-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.getElementById('continueBtn').disabled = true;
    document.getElementById('chatBtn').disabled = true;
}

// Sound Effect
function playClickSound() {
    const sound = document.getElementById('clickSound');
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(() => {});
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // ESC key to go back
    if (e.key === 'Escape') {
        const activeScreen = document.querySelector('.screen.active');
        if (activeScreen && activeScreen.id !== 'welcomeScreen') {
            goBack();
        }
    }

    // Enter key to continue (when button is enabled)
    if (e.key === 'Enter') {
        const activeScreen = document.querySelector('.screen.active');
        if (!activeScreen) return;

        if (activeScreen.id === 'warningScreen') {
            const continueBtn = document.getElementById('continueBtn');
            if (continueBtn && !continueBtn.disabled) {
                showPhoneInput();
            }
        } else if (activeScreen.id === 'phoneScreen') {
            const chatBtn = document.getElementById('chatBtn');
            if (chatBtn && !chatBtn.disabled) {
                openWhatsApp();
            }
        }
    }
});

// Prevent form submission on Enter in input fields
document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && this.tagName !== 'TEXTAREA') {
                e.preventDefault();
            }
        });
    });
});

// Console Easter eggs
console.log('%c💔 Ex Chat Portal 💔', 'font-size: 30px; color: #d63031; font-weight: bold;');
console.log('%cBe brave. Be kind. Be honest.', 'font-size: 16px; color: #6c5ce7;');
console.log('%cMade with ❤️ (and a bit of heartbreak)', 'font-size: 12px; color: #95a5a6;');
