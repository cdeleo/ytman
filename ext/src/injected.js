(function() {
  
const YTMAN_EXT_ID = 'ellkbkflcogpfdnbihlnkafbbhfkdefa';

// Adapted from https://stackoverflow.com/a/29939024
function base64ToBlob(base64, mimetype, slicesize) {
  if (!window.atob || !window.Uint8Array) {
    // The current browser doesn't have the atob function.
    return null;
  }
  mimetype = mimetype || '';
  slicesize = slicesize || 512;

  base64 = base64.replace(
      new RegExp('-', 'g'), '+').replace(new RegExp('_', 'g'), '/');

  const bytechars = atob(base64);
  const bytearrays = [];
  for (let offset = 0; offset < bytechars.length; offset += slicesize) {
    const slice = bytechars.slice(offset, offset + slicesize);
    const bytenums = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      bytenums[i] = slice.charCodeAt(i);
    }
    const bytearray = new Uint8Array(bytenums);
    bytearrays[bytearrays.length] = bytearray;
  }
  return new Blob(bytearrays, {type: mimetype});
}
  
function connectToExt() {
  const port = chrome.runtime.connect(YTMAN_EXT_ID);
  port.onMessage.addListener(message => {
    if (message.thumbnail) {
      const thumbnailBlob = base64ToBlob(message.thumbnail, 'image/png');
      const fileInput = document.querySelector('#file-loader');
      Object.defineProperty(
        fileInput, 'files', {get: () => [thumbnailBlob], configurable: true});
      fileInput.dispatchEvent(new Event('change'));
    }
    if (message.description) {
      const descriptionBox = document.querySelector('.description textarea');
      descriptionBox.value = message.description;
    }
  });
}

connectToExt();
})();