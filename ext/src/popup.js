const THUMBNAILS_APP_ID = 'thumbnails-dot-youtube-manager-196811';
const BG_KEY = 'ahhifnlvdXR1YmUtbWFuYWdlci0xOTY4MTFyLAsSBFVzZXIiFTEwNDU5MzMwNzY2MDA0NTU1OTQxNAwLEgVJbWFnZRiRi0AM';

let port = null;

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function getThumbnail(bgKey, title, subtitle, callback) {
  chrome.identity.getAuthToken({interactive: true}, token => {
    const params = new URLSearchParams({
      bg_key: bgKey,
      title: title,
      subtitle: subtitle
    });
    fetch(
        apiUrl(THUMBNAILS_APP_ID, 'thumbnails', 'v1', 'get') + '?' + params.toString(),
        {headers: {Authorization: 'Bearer ' + token}})
      .then(res => res.json())
      .then(data => callback(data.image_data));
  });
}

function loadData(data) {
  document.querySelector('#title').innerText = data.title;
}

function handleDone() {
  if (port) {
    getThumbnail(BG_KEY, 'title', 'subtitle', data => {
      port.postMessage(data);
    });
  }
}

chrome.runtime.onMessage.addListener(
  request => {
    switch (request.type) {
      case 'LOAD_DATA':
        loadData(request.data);
        break;
    }
  }
);

chrome.runtime.onConnectExternal.addListener(p => port = p);
document.querySelector('#done').addEventListener('click', handleDone);

chrome.tabs.executeScript({file: 'src/content-script.js'});