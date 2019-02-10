(function() {
const APP_ID = 'backend-dot-youtube-manager-196811';

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function sendLoadDataMessage() {
  loadDataMessage = {
    type: 'LOAD_DATA',
    data: {
      title: document.querySelector('div.title textarea').value
    }
  };
  chrome.runtime.sendMessage(loadDataMessage);
}

function injectPageScript() {
  const injectedScript = document.createElement('script');
  injectedScript.src = chrome.extension.getURL('src/injected.js');
  injectedScript.onload = function() {
    this.remove();
  };
  document.documentElement.appendChild(injectedScript);
}

sendLoadDataMessage();
injectPageScript();
})();