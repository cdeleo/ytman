const e = React.createElement;

let port = null;

async function createThumbnail(data) {
  const backgroundImg = new Image();
  const background = new Promise(resolve => {
    backgroundImg.onload = () => resolve(backgroundImg);
  });
  backgroundImg.src = data.getImageData();

  const canvas = document.querySelector('#thumbnail-render');
  const c = canvas.getContext('2d');

  const renderer = new SvgRenderer('templates/azorius.svg');
  const valueMap = {
    title: data.title,
    subtitle: data.subtitle,
  };
  await renderer.render(c, background, valueMap);

  const renderedData = canvas.toDataURL();
  const prefix = 'data:image/png;base64,';
  if (renderedData.startsWith(prefix)) {
    return renderedData.substr(prefix.length);
  } else {
    return renderedData;
  }
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

function renderDescription(template, valueMap) {
  let desc = template;
  for (key in valueMap) {
    desc = desc.replace('{' + key + '}', valueMap[key]);
  }
  return desc;
}

function getDescription(valueMap) {
  return new Promise(resolve => {
    chrome.storage.sync.get('desc', items => resolve(items.desc));
  }).then(desc => renderDescription(desc, valueMap));
}

function handleDone(data) {
  if (port) {
    data.onUpdate({ message: 'Generating thumbnail...' });
    const setThumbnail = createThumbnail(data)
      .then(thumbnail => port.postMessage({ thumbnail: thumbnail }));
    const setDescription = getDescription(getValueMap(data.cardData))
      .then(desc => port.postMessage({ description: desc }));
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