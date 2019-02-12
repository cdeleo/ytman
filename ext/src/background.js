chrome.runtime.onInstalled.addListener(() => {
  chrome.declarativeContent.onPageChanged.removeRules(undefined, () => {
    chrome.declarativeContent.onPageChanged.addRules([
      {
        conditions: [
          new chrome.declarativeContent.PageStateMatcher({
            pageUrl: { urlContains: 'https://studio.youtube.com/video/' },
          })
        ],
        actions: [new chrome.declarativeContent.ShowPageAction()],
      }
    ]);
  });
});