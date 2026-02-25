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
                    if (data[id].text !== undefined) element.innerHTML = data[id].text;
                    if (data[id].color !== undefined) element.style.color = data[id].color;
                    if (data[id].fontSize !== undefined) element.style.fontSize = data[id].fontSize;
                }
            });
        }

        // Handle Preview Highlighting
        const params = new URLSearchParams(window.location.search);
        const previewId = params.get('preview');
        if (previewId && !window.hasPreviewedSitemap) {
            window.hasPreviewedSitemap = true; // prevent re-running on subsequent firebase syncs

            const previewElem = document.querySelector(`[data-content-id="${previewId}"]`);
            if (previewElem) {
                // Wait a tiny bit for render
                setTimeout(() => {
                    previewElem.scrollIntoView({ behavior: 'smooth', block: 'center' });

                    // Highlight effect
                    const originalBg = previewElem.style.backgroundColor;
                    const originalTrans = previewElem.style.transition;
                    const originalOutline = previewElem.style.outline;
                    const originalOutlineOffset = previewElem.style.outlineOffset;

                    previewElem.style.transition = 'background-color 0.5s ease';
                    previewElem.style.backgroundColor = '#fef08a'; // Tailwind yellow-200
                    previewElem.style.outline = '4px solid #eab308'; // Tailwind yellow-500
                    previewElem.style.outlineOffset = '2px';
                    previewElem.style.borderRadius = '4px';

                    setTimeout(() => {
                        previewElem.style.backgroundColor = originalBg;
                        previewElem.style.outline = originalOutline;
                        previewElem.style.outlineOffset = originalOutlineOffset;
                        setTimeout(() => previewElem.style.transition = originalTrans, 500);
                    }, 3000); // 3 seconds highlight
                }, 300);
            }
        }
    });
});
