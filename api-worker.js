/**
 * api-worker.js
 * This script runs in a separate thread to handle all API calls,
 * preventing the main UI thread from freezing.
 */

self.onmessage = async (event) => {
    const { id, apiUrl, payload, apiKey } = event.data;

    // Use direct API URL with key in headers
    const newApiUrl = apiUrl;

    try {
        const result = await callGenerativeApi(newApiUrl, payload, apiKey);
        // Send success result back to the main thread
        self.postMessage({ id, success: true, result });
    } catch (error) {
        // Send error back to the main thread
        self.postMessage({ id, success: false, error: error.message });
    }
};

/**
 * Centralized function to call Google Generative AI APIs.
 * This is the same robust function from the main thread, now living in the worker.
 * @param {string} apiUrl - The full API endpoint URL.
 * @param {object} payload - The request payload to be sent as JSON.
 * @param {string} apiKey - The user's API key.
 * @returns {Promise<any>} The JSON response from the API.
 */
const callGenerativeApi = async (apiUrl, payload, apiKey) => {
    if (!apiKey) {
        throw new Error("Clave de API no configurada en el worker.");
    }
    console.log(`[Worker] Calling API: ${apiUrl.split('?')[0]}`);

    let response;
    let retries = 3;
    let delay = 1000;

    for (let i = 0; i < retries; i++) {
        try {
            console.log(`[Worker] Attempt ${i + 1}...`);
            response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-goog-api-key': apiKey
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errorText = `Error en la API: ${response.status}`;
                try {
                    const errorBody = await response.json();
                    const message = errorBody.error?.message || JSON.stringify(errorBody);
                    errorText = `Error en la API: ${response.status} - ${message}`;
                } catch (e) {
                    // If the error response isn't JSON, use the status text.
                    errorText = `Error en la API: ${response.status} - ${response.statusText}`;
                }
                throw new Error(errorText);
            }

            // The worker just returns the raw JSON result.
            // The main thread will be responsible for parsing it.
            return await response.json();

        } catch (error) {
            console.warn(`[Worker] Intento ${i + 1} fallido. Reintentando en ${delay}ms...`, error.message);
            if (i === retries - 1) {
                // After all retries, throw the final error.
                throw error;
            }
            // Wait before retrying
            await new Promise(res => setTimeout(res, delay));
            delay *= 2; // Exponential backoff
        }
    }
};