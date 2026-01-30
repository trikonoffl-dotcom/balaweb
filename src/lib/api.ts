export const getApiUrl = (path: string) => {
    // In development, use relative path (proxy)
    // In production, use the environment variable
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

    // Debugging: Log where we are trying to connect
    console.log(`[API Debug] Calling: ${baseUrl}${path}`);
    if (!baseUrl && path.startsWith('/api')) {
        console.warn("[API Warning] NEXT_PUBLIC_API_URL is missing! Requests may fail.");
    }

    return `${baseUrl}${path}`;
}
