function getMap(params) {
    const baseUrl = '/get_map';
    const urlObj = new URL(baseUrl, window.location.origin);
    Object.keys(params).forEach(key => urlObj.searchParams.append(key, params[key]));

    return fetch(urlObj, {
        method: 'GET' // Explicitly specifying the GET method
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Check if the response is a redirect
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        // Extract filename from Content-Disposition header
        const disposition = response.headers.get('Content-Disposition');
        let filename = '';
        if (disposition && disposition.includes('attachment')) {
            const parts = disposition.split(';');
            for (let part of parts) {
                part = part.trim();
                if (part.startsWith('filename=')) {
                    filename = part.split('=')[1].replace(/['"]/g, '');
                    break;
                }
            }
        }
        // Create a blob from the response
        return response.blob().then(blob => ({ blob, filename }));
    })
    .then(({ blob, filename }) => {
        if (blob) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || 'download'; // Use the extracted filename or a default name
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
