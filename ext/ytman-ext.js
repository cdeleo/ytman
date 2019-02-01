const UPLOADER_TAG = 'ytcp-thumbnails-compact-editor-uploader';

const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node.tagName && node.tagName.toLowerCase() == UPLOADER_TAG) {
        console.log('Target:' + mutation.target.tagName);
        console.log(mutation);
      }
    });
  });
});
observer.observe(document.documentElement, {childList: true, subtree: true});
