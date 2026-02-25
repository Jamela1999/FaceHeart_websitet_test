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

                    // Recursively reveal hidden parents (e.g. mega menus)
                    const hiddenParents = [];
                    let p = previewElem.parentElement;
                    while (p && p !== document.body && p !== document.documentElement) {
                        const style = window.getComputedStyle(p);
                        let needsReveal = false;
                        if (style.opacity === '0' || style.visibility === 'hidden' || style.display === 'none') {
                            hiddenParents.push({
                                el: p,
                                opacity: p.style.opacity,
                                visibility: p.style.visibility,
                                display: p.style.display,
                                pointerEvents: p.style.pointerEvents,
                                zIndex: p.style.zIndex
                            });
                            p.style.opacity = '1';
                            p.style.visibility = 'visible';
                            if (style.display === 'none') p.style.display = 'block';
                            p.style.pointerEvents = 'auto';
                            p.style.zIndex = '999999';
                        }
                        p = p.parentElement;
                    }

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

                        // Restore hidden parents
                        hiddenParents.forEach(saved => {
                            saved.el.style.opacity = saved.opacity;
                            saved.el.style.visibility = saved.visibility;
                            saved.el.style.display = saved.display;
                            saved.el.style.pointerEvents = saved.pointerEvents;
                            saved.el.style.zIndex = saved.zIndex;
                        });
                    }, 4000); // 4 seconds highlight
                }, 400);
            }
        }
    });
});
