let auth = null;

function handleClientLoad() {
  gapi.load('client:auth2', initClient);
}

function initClient() {
  const params = {
    discoveryDocs: ['https://datastore-dot-youtube-manager-196811.appspot.com/_ah/api/discovery/v1/apis/images/v1/rest'],
    client_id: '955262123852-c1gthms5mhs36q6njvg6kgqu4f1b09q7.apps.googleusercontent.com',
    scope: 'https://www.googleapis.com/auth/userinfo.email'
  };
  gapi.client.init(params).then(function() {
    auth = gapi.auth2.getAuthInstance();
    auth.isSignedIn.listen(handleSigninState);
    handleSigninState(auth.isSignedIn.get());
  });
}

function handleSigninState(isSignedIn) {
  document.querySelectorAll('.signedin').forEach(function(item) {
    item.style.display = isSignedIn ? 'block' : 'none';
  });
  document.querySelectorAll('.signedout').forEach(function(item) {
    item.style.display = isSignedIn ? 'none' : 'block';
  });
}

function validateCreate(cropper) {
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
  const container = document.querySelector('#cropperPane');
  const canvas = document.createElement('canvas');
  canvas.width = container.clientWidth;
  container.appendChild(canvas);
  const renderCanvas = document.createElement('canvas');
  renderCanvas.style.display = 'none';
  container.appendChild(renderCanvas);
  cropper = new Cropper(canvas, renderCanvas);

  const signinButton = document.querySelector('#signinButton');
  signinButton.addEventListener('click', function(e) {
    if (auth != null) {
      auth.signIn();
    }
  });

  const signoutButton = document.querySelector('#signoutButton');
  signoutButton.addEventListener('click', function(e) {
    if (auth != null) {
      auth.signOut();
    }
  });

  const imageInput = document.querySelector('#imageInput');
  imageInput.addEventListener('change', function(e) {
    if (e.target.files.length == 0) {
      return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
      const image = new Image();
      image.addEventListener('load', function() {
        canvas.width = container.clientWidth;
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
    if (validateCreate(cropper)) {
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
