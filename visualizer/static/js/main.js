$(document).ready(function() {
    // Handle form submission
    $('#data-form').submit(function(e) {
        e.preventDefault();
        
        // Show loading indicator
        $('#loading').removeClass('d-none');
        $('#result-container').addClass('d-none');
        $('#error-container').addClass('d-none');
        
        // Get form data
        const formData = $(this).serialize();
        
        // Send AJAX request
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            dataType: 'json',
            success: function(response) {
                // Hide loading indicator
                $('#loading').addClass('d-none');
                
                if (response.success) {
                    // Show result container
                    $('#result-container').removeClass('d-none');
                    
                    // Format and display the result
                    const resultHtml = `<div class="mb-3">
                        <h6>Extracted Data:</h6>
                        <pre class="bg-light p-2 rounded">${JSON.stringify(response.data, null, 2)}</pre>
                    </div>`;
                    
                    $('#result-content').html(resultHtml);
                    
                    // Show visualization suggestion if available
                    if (response.data.visualization_type) {
                        $('#viz-suggestion').html(`
                            <strong>Suggested Visualization:</strong> ${response.data.visualization_type}
                        `);
                    } else {
                        $('#viz-suggestion').html(`
                            <strong>Processed Successfully!</strong> Ready for visualization.
                        `);
                    }
                    
                    // Update result link
                    $('#view-result').attr('href', `/result/${response.id}/`);
                    
                    // Update Unity link
                    $('#unity-link').attr('href', `unity://open?id=${response.id}`);
                } else {
                    // Show error message
                    $('#error-container').removeClass('d-none');
                    $('#error-message').text(response.error || 'An unknown error occurred.');
                }
            },
            error: function(xhr, status, error) {
                // Hide loading indicator
                $('#loading').addClass('d-none');
                
                // Show error message
                $('#error-container').removeClass('d-none');
                $('#error-message').text('Server error: ' + error);
            }
        });
    });
    
    // Unity launch buttons
    $('.unity-link, #unity-button').on('click', function(e) {
        e.preventDefault();
        const id = $(this).data('id');
        window.location.href = `unity://open?id=${id}`;
    });
});