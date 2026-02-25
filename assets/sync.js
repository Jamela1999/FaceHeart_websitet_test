// Wait for Firebase to initialize
document.addEventListener("DOMContentLoaded", () => {
    if (typeof database === 'undefined') {
        console.error("Firebase is not initialized. Please configure assets/firebase-config.js.");
        return;
    }

    const sitemapRef = database.ref('sitemap/content');

    // Fetch existing overrides and update the DOM
    sitemapRef.on('value', (snapshot) => {
        const data = snapshot.val();
        if (data) {
            Object.keys(data).forEach(id => {
                const element = document.querySelector(`[data-content-id="${id}"]`);
                if (element) {
                    element.innerHTML = data[id];
                }
            });
        }
    });
});
