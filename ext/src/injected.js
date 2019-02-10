loadDataMessage = {
  type: 'LOAD_DATA',
  data: {
    title: document.querySelector('div.title textarea').value
  }
};
chrome.runtime.sendMessage(loadDataMessage);