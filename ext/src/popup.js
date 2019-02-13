const BACKEND_APP_ID = 'backend-dot-youtube-manager-196811';
const THUMBNAILS_APP_ID = 'thumbnails-dot-youtube-manager-196811';
const BG_KEY = 'ahhifnlvdXR1YmUtbWFuYWdlci0xOTY4MTFyLAsSBFVzZXIiFTEwNDU5MzMwNzY2MDA0NTU1OTQxNAwLEgVJbWFnZRiRi0AM';

const e = React.createElement;

let port = null;

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function createImage(data, name, mid, callback) {
  chrome.identity.getAuthToken({interactive: true}, token => {
    const params = new URLSearchParams({
      data: data,
      name: name,
    });
    if (mid) {
      params.metadata = [{key: 'mid', value: parseInt(mid)}];
    }
    fetch(
        apiUrl(BACKEND_APP_ID, 'ytman', 'v1', 'images/create'),
        {
          method: 'POST',
          headers: {Authorization: 'Bearer ' + token},
          body: params,
        })
      .then(res => res.json())
      .then(data => callback(data.image));
  });
}

function getThumbnail(bgKey, title, subtitle, callback) {
  chrome.identity.getAuthToken({interactive: true}, token => {
    const params = new URLSearchParams({
      bg_key: bgKey,
      title: title,
      subtitle: subtitle,
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

function startGetThumbnail(data, imageKey) {
  data.onUpdate({message: 'Generating thumbnail...'});
  getThumbnail(imageKey, data.title, data.subtitle, thumbnail => {
    port.postMessage(thumbnail);
    data.onUpdate({message: 'Done!'});
    window.close();
  });
}

function handleDone(data) {
  console.log(data);
  if (port) {
    switch (data.image.type) {
      case 'new':
        data.onUpdate({message: 'Creating image...'});
        createImage(
          data.image.data,
          data.image.name,
          data.image.mid,
          image => startGetThumbnail(data, image.key));
        break;
      case 'existing':
        startGetThumbnail(data, data.image.key);
        break;
    }
  }
}

chrome.runtime.onConnectExternal.addListener(p => port = p);
chrome.tabs.executeScript({file: 'src/content-script.js'});
ReactDOM.render(
  e(ThumbnailCreator, {onDone: data => handleDone(data)}),
  document.querySelector('#thumbnail-creator'));