(function (root) {
  function createLoader(fetcher) {
    const pending = new Map();
    function load(url) {
      if (!url) return Promise.reject(new Error('Missing asset URL'));
      if (!pending.has(url)) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);
        const request = Promise.resolve().then(() => fetcher(url, { signal: controller.signal }))
          .then(response => {
            if (!response.ok) throw new Error(`Asset request failed: ${response.status}`);
            return response.json();
          }).catch(error => { pending.delete(url); throw error; })
          .finally(() => clearTimeout(timeout));
        pending.set(url, request);
      }
      return pending.get(url);
    }
    return { load };
  }
  root.PAPERNOTE_ASSETS = createLoader((...args) => fetch(...args));
  if (typeof module !== 'undefined') module.exports = { createLoader };
})(typeof window === 'undefined' ? globalThis : window);
