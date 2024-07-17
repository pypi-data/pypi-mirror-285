DEFAULT_MANIFEST = """
{
    "version": "1.0.0",
    "manifest_version": 3,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "webRequest",
        "webRequestAuthProvider"
    ],
    "background": {
        "service_worker": "background.js"
    },
    "host_permissions": [
        "<all_urls>"
    ],
    "minimum_chrome_version":"22.0.0"
}
"""

DEFAULT_BACKGROUND_JS_PROXY = """
const config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "%s",
            host: "%s",
            port: %s
        }
    }
}
chrome.proxy.settings.set({
    value: config,
    scope: 'regular'
}, () => {});
"""

DEFAULT_BACKGROUND_AUTO_AUTH = """
chrome.webRequest.onAuthRequired.addListener(
  (details, callback) => {
    const authCredentials = {
      username: "%s",
      password: "%s",
    };
    setTimeout(() => {
      callback({ authCredentials });
    }, 200);
  },
  { urls: ["<all_urls>"] },
  ["asyncBlocking"]
);

"""
