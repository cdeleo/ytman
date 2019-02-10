// const APP_ID = 'backend-dot-youtube-manager-196811';

// function apiUrl(appId, api, version, method) {
//   return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
// }

// chrome.identity.getAuthToken({interactive: true}, (token) => {
//   console.log(token);
//   fetch(
//       apiUrl(APP_ID, 'ytman', 'v1', 'images/list'),
//       {headers: {Authorization: 'Bearer ' + token}}).then((response) => {
//     response.json().then(data => {
//       const listContainer = document.querySelector('#image-list');
//       data.images.forEach(image => {
//         const imageItem = document.createElement('li');
//         imageItem.innerText = image.name;
//         listContainer.appendChild(imageItem);
//       });
//     });
//   });
// });

function loadData(data) {
  document.querySelector('#title').innerText = data.title;
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
console.log('listening');
chrome.tabs.executeScript({file: 'src/injected.js'});