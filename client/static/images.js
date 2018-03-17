let cropper = null;

function initApi() {
  gapi.client.load(
      'images', 'v1', null,
      'https://datastore-dot-youtube-manager-196811.appspot.com/_ah/api');
}

function validateCreate() {
  if (cropper == null || !cropper.hasImage()) {
    alert('No image is selected.');
    return false;
  }
  if (document.querySelector('#nameField').value == '') {
    alert('Name is required.');
    return false;
  }
  if (document.querySelector('#midField').value != '') {
    if (isNaN(parseInt(document.querySelector('#midField').value))) {
      alert('MID must be an integer if provided.');
      return false;
    }
  }
  return true;
}

(function() {
  const container = document.querySelector('#cropper');
  const canvas = document.createElement('canvas');
  canvas.width = container.clientWidth;
  container.appendChild(canvas);
  const renderCanvas = document.createElement('canvas');
  renderCanvas.style.display = 'none';
  container.appendChild(renderCanvas);
  cropper = new Cropper(canvas, renderCanvas);

  const imageInput = document.querySelector('#imageInput');
  imageInput.addEventListener('change', function(e) {
    if (e.target.files.length == 0) {
      return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
      const image = new Image();
      image.addEventListener('load', function() {
        cropper.setImage(image);
      });
      image.src = e.target.result;
    }
    reader.readAsDataURL(e.target.files[0]);
  });

  const resetButton = document.querySelector('#resetButton');
  resetButton.addEventListener('click', function(e) {
    cropper.resetMask();
  });

  const doneButton = document.querySelector('#doneButton');
  doneButton.addEventListener('click', function(e) {
    if (validateCreate()) {
      const req = {
          'name': document.querySelector('#nameField').value,
          'data': cropper.render()
      };
      const mid = document.querySelector('#midField').value;
      if (mid != '') {
        req.metadata = [{'key': 'mid', 'value': parseInt(mid).toString()}];
      }
      gapi.client.images.create(req).execute(function(resp) {
        console.log(resp);
      });
    }
  });
})();
