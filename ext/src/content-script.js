(function() {
const APP_ID = 'backend-dot-youtube-manager-196811';

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function sendLoadDataMessage() {
  const rawTitle = document.querySelector('div.title textarea').value;
  const titleTokens = rawTitle.split(' - ');
  loadDataMessage = {
    type: 'LOAD_DATA',
    data: {
      title: titleTokens[0],
      subtitle: titleTokens[1] || ''
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