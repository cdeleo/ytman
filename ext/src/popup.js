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

function getValueMap(cardData) {
  if (cardData) {
    return {
      name: cardData.name,
      artist: cardData.artist,
      company: 'Wizards of the Coast LLC, a subsidiary of Hasbro, Inc.',
      year: cardData.released_at.substring(0, 4),
    };
  }
  return {};
}

function getDescription(valueMap) {
  return (
    `Thumbnail from ${valueMap.name} by ${valueMap.artist}\n` +
    `\u00A9 ${valueMap.year} ${valueMap.company}\n\n` +
    `Intro by Carbot Animations`
  );
}

function handleDone(data) {
  if (port) {
    port.postMessage({ description: getDescription(getValueMap(data.cardData)) });
    data.onUpdate({ message: 'Generating thumbnail...' });
    const setThumbnail = createThumbnail(data)
      .then(thumbnail => port.postMessage({ thumbnail: thumbnail }))
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