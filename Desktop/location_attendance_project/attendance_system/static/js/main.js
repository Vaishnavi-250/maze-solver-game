// GPS Location Tracking
const LocationTracker = {
    latitude: null,
    longitude: null,
    accuracy: null,
    map: null,
    userMarker: null,
    officeMarker: null,

    // Get current position
    getCurrentLocation: function() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject("Geolocation is not supported by your browser");
                return;
            }

            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.latitude = position.coords.latitude;
                    this.longitude = position.coords.longitude;
                    this.accuracy = position.coords.accuracy;
                    resolve({
                        latitude: this.latitude,
                        longitude: this.longitude,
                        accuracy: this.accuracy
                    });
                },
                (error) => {
                    reject("Error: " + error.message);
                },
                options
            );
        });
    },

    // Initialize map
    initMap: function(containerId, latitude, longitude, officeLatitude, officeLongitude) {
        if (document.getElementById(containerId)) {
            this.map = L.map(containerId).setView([latitude, longitude], 15);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // User marker
            this.userMarker = L.circleMarker([latitude, longitude], {
                color: '#ec407a',
                fillColor: '#f06292',
                fillOpacity: 0.8,
                radius: 10,
                weight: 2
            }).addTo(this.map).bindPopup('<b>Your Location</b>');

            // Office marker
            if (officeLatitude && officeLongitude) {
                this.officeMarker = L.marker([officeLatitude, officeLongitude], {
                    icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    })
                }).addTo(this.map).bindPopup('<b>Office Location</b>');
            }
        }
    },

    // Update location in hidden fields
    updateLocationFields: function(latitudeFieldId, longitudeFieldId) {
        const latField = document.getElementById(latitudeFieldId);
        const lonField = document.getElementById(longitudeFieldId);
        
        if (latField && lonField) {
            latField.value = this.latitude;
            lonField.value = this.longitude;
        }
    },

    // Calculate distance
    calculateDistance: function(lat1, lon1, lat2, lon2) {
        const R = 6371000; // Earth's radius in meters
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.asin(Math.sqrt(a));
        return Math.round(c * R);
    },

    // Format distance for display
    formatDistance: function(meters) {
        if (meters < 1000) {
            return meters + " m";
        }
        return (meters / 1000).toFixed(2) + " km";
    }
};

// Utility Functions
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'loadingSpinner';
    spinner.className = 'spinner-border text-pink';
    spinner.style.position = 'fixed';
    spinner.style.top = '50%';
    spinner.style.left = '50%';
    spinner.style.transform = 'translate(-50%, -50%)';
    spinner.style.color = '#ec407a';
    spinner.style.zIndex = '9999';
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.remove();
    }
}

// Format time for display
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Check-in/Check-out handler
function handleAttendanceSubmit(event, isCheckIn = true) {
    event.preventDefault();
    
    showLoadingSpinner();
    
    LocationTracker.getCurrentLocation()
        .then((location) => {
            document.querySelector('input[name="latitude"]').value = location.latitude;
            document.querySelector('input[name="longitude"]').value = location.longitude;
            hideLoadingSpinner();
            event.target.submit();
        })
        .catch((error) => {
            hideLoadingSpinner();
            showAlert('Error getting location: ' + error, 'danger');
        });
}

// Show alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to page load
    document.body.classList.add('fade-in');
});
