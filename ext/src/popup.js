const e = React.createElement;

let port = null;

function createThumbnail(data) {
  const background = new Image();
  const backgroundReady = new Promise(resolve => {
    background.onload = resolve;
  });
  background.src = data.getImageData();

  const svgString = fetch('templates/orange.svg')
    .then(response => response.text());

  const canvas = document.querySelector('#thumbnail-render');
  const c = canvas.getContext('2d');

  return Promise.all([background, svgString])
    .then(values => {
      const parser = new DOMParser();
      const fontMap = { 'Aharoni': 'url(fonts/ahronbd-webfont.woff)' };
      const renderer = new SvgRenderer(parser, values[1], fontMap);

      const valueMap = {
        title: data.title,
        subtitle: data.subtitle,
        background: background,
      };
      return renderer.render(c, valueMap);
    })
    .then(() => canvas.toDataURL())
    .then(data => {
      const prefix = 'data:image/png;base64,';
      if (data.startsWith(prefix)) {
        return data.substr(prefix.length);
      } else {
        return data;
      }
    });
}

function handleDone(data) {
  if (port) {
    data.onUpdate({ message: 'Generating thumbnail...' });
    const setThumbnail = createThumbnail(data)
      .then(thumbnail => port.postMessage({ thumbnail: thumbnail }));
    const setDescription = data.getDescription()
      .then(description => {
        if (description) {
          port.postMessage({ description: description });
        }
      });
    Promise.all([setThumbnail, setDescription])
      .then(() => {
        data.onUpdate({ message: 'Done!' });
        window.close();
      });
  }
}

chrome.runtime.onConnectExternal.addListener(p => port = p);
chrome.tabs.executeScript({ file: 'src/content-script.js' });
ReactDOM.render(
  e(ThumbnailCreator, { onDone: data => handleDone(data) }),
  document.querySelector('#thumbnail-creator'));