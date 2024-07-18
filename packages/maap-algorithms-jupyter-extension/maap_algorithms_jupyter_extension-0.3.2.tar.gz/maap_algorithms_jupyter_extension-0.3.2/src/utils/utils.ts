export async function checkUrlExists(url) {
    try {
        const response = await fetch(url, { method: 'HEAD' });

        if (response.ok) {
            console.log(`URL "${url}" exists.`);
            return true
        } else {
            console.log(`URL "${url}" returned status code ${response.status}.`);
        }
    } catch (error) {
        console.error('Error checking URL existence:', error);
        return false
    }
    return false
}