(function () {

  function sendLoadDataMessage() {
    const rawTitle = document.querySelector('div.title #textbox').innerText;
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
    injectedScript.onload = function () {
      this.remove();
    };
    document.documentElement.appendChild(injectedScript);
  }

  sendLoadDataMessage();
  injectPageScript();
})();