const THUMBNAILS_APP_ID = 'thumbnails-dot-youtube-manager-196811';
const BG_KEY = 'ahhifnlvdXR1YmUtbWFuYWdlci0xOTY4MTFyLAsSBFVzZXIiFTEwNDU5MzMwNzY2MDA0NTU1OTQxNAwLEgVJbWFnZRiRi0AM';

const e = React.createElement;

let port = null;

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function getThumbnail(bgKey, title, subtitle) {
  return new Promise((resolve, reject) => {
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
        .then(data => resolve(data.image_data))
        .catch(e => reject(e));
    });
  });
}

function loadData(data) {
  document.querySelector('#title').innerText = data.title;
}

function handleDone(data) {
  if (port) {
    data.onUpdate({message: 'Creating image...'});
    const setThumbnail = data.getBgKey()
      .then(bgKey => {
        data.onUpdate({message: 'Generating thumbnail...'});
        return getThumbnail(bgKey, data.title, data.subtitle);
      })
      .then(thumbnail => port.postMessage({thumbnail: thumbnail}));
    const setDescription = data.getDescription()
      .then(description => {
        if (description) {
          port.postMessage({description: description});
        }
      });
    Promise.all([setThumbnail, setDescription])
      .then(() => {
        data.onUpdate({message: 'Done!'});
        window.close();
      });
  }
}

chrome.runtime.onConnectExternal.addListener(p => port = p);
chrome.tabs.executeScript({file: 'src/content-script.js'});
ReactDOM.render(
  e(ThumbnailCreator, {onDone: data => handleDone(data)}),
  document.querySelector('#thumbnail-creator'));