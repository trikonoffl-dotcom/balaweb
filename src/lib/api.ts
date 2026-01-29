export const getApiUrl = (path: string) => {
    // In development, use relative path (proxy)
    // In production, use the environment variable
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    return `${baseUrl}${path}`;
}
