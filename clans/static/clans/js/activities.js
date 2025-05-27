async function deleteActivity(activityType, recordId) {
    if (!confirm('Are you sure you want to delete this record?')) {
        return;
    }

    try {
        const response = await fetch(`/api/activities/${activityType}/${recordId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Remove the row from DOM
        const row = document.getElementById(`record-row-${recordId}`);
        if (row) {
            row.remove();
        } else {
            location.reload(); // Fallback if row not found
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete activity');
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}