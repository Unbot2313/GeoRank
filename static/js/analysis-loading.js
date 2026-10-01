// Loading state for forms that run a website analysis (scrape + AI), which can take up to a minute.
// Markup: <form data-analysis-form> with a [data-loading-button] and the analysis_progress.html partial.
// The request is synchronous, so the step messages advance on a timer, not on real progress.
(() => {
    // Seconds after submit at which each message appears.
    const STEPS = [
        [0, 'Fetching the website…'],
        [4, 'Reading the content…'],
        [8, 'Asking the AI how it sees the site…'],
        [18, 'Calculating scores and recommendations…'],
        [35, 'Almost done…'],
    ];

    document.querySelectorAll('form[data-analysis-form]').forEach((form) => {
        const button = form.querySelector('[data-loading-button]');
        const spinner = form.querySelector('[data-loading-spinner]');
        const label = form.querySelector('[data-loading-label]');
        const progress = form.querySelector('[data-analysis-progress]');
        const step = form.querySelector('[data-analysis-step]');
        const inputs = form.querySelectorAll('input:not([type="hidden"])');
        const idleText = label.textContent;
        const disabledByServer = button.disabled;
        let timers = [];

        function setLoading(loading) {
            button.disabled = loading || disabledByServer;
            // While loading the button keeps its color with a wait cursor, not the faded "not allowed" look.
            button.classList.toggle('disabled:opacity-50', !loading);
            button.classList.toggle('disabled:cursor-not-allowed', !loading);
            button.classList.toggle('cursor-wait', loading);
            inputs.forEach((input) => { input.readOnly = loading; });
            form.setAttribute('aria-busy', loading);
            spinner.classList.toggle('hidden', !loading);
            progress.classList.toggle('hidden', !loading);
            label.textContent = loading ? 'Analyzing…' : idleText;
            timers.forEach(clearTimeout);
            timers = loading
                ? STEPS.map(([sec, text]) => setTimeout(() => { step.textContent = text; }, sec * 1000))
                : [];
        }

        form.addEventListener('submit', () => setLoading(true));

        // Coming back with the browser's Back button restores the page from cache: reset it.
        window.addEventListener('pageshow', (e) => {
            if (e.persisted) setLoading(false);
        });
    });
})();
