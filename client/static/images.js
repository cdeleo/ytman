// Cropper

const HANDLE_SIZE = 10;
const PADDING = 10;
const TARGET_WIDTH = 1280;
const TARGET_HEIGHT = 720;
const TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT;

const Elements = Object.freeze({
    NONE: 'none',
    MASK: 'mask',
    NW_HANDLE: 'nwHandle',
    NE_HANDLE: 'neHandle',
    SE_HANDLE: 'seHandle',
    SW_HANDLE: 'swHandle',
});

function Handle(x, y, element) {
  this.x = x;
  this.y = y;
  this.element = element;

  this.addPath = function(c) {
    c.rect(
        this.x - HANDLE_SIZE / 2,
        this.y - HANDLE_SIZE / 2,
        HANDLE_SIZE,
        HANDLE_SIZE);
  }
}

function Mask(x, y, width) {
  this.x = x;
  this.y = y;
  this.width = width;
  this.element = Elements.MASK;

  this.height = function() {
    return this.width / TARGET_RATIO;
  }

  this.addPath = function(c) {
    c.rect(this.x, this.y, this.width, this.height());
  }
}

function Cropper(canvas, renderCanvas) {
  
  this.CURSOR_MAP = new Map([
      [Elements.NONE, 'default'],
      [Elements.MASK, 'move'],
      [Elements.NW_HANDLE, 'nw-resize'],
      [Elements.NE_HANDLE, 'ne-resize'],
      [Elements.SE_HANDLE, 'se-resize'],
      [Elements.SW_HANDLE, 'sw-resize'],
  ]);

  this.canvas = canvas;
  this.renderCanvas = renderCanvas;
  this.c = canvas.getContext('2d');
  this.image = null;
  this.imageScale = null;
  this.mask = null;
  this.handles = null;
  this.draggingElement = Elements.NONE;

  this.areaWidth = function() {
    return this.canvas.width - 2 * PADDING;
  }

  this.areaHeight = function() {
    return this.canvas.height - 2 * PADDING;
  }

  this.setImage = function(image) {
    this.image = image;
    this.imageScale = (this.canvas.width - 2 * PADDING) / image.width;
    this.canvas.height = this.imageScale * image.height + 2 * PADDING;
    this.c.setTransform(1, 0, 0, 1, PADDING, PADDING);
    this.resetMask();
  }

  this.drawImage = function() {
    this.c.save();
    this.c.clearRect(
        -1 * PADDING, -1 * PADDING, this.canvas.width, this.canvas.height);
    this.c.scale(this.imageScale, this.imageScale);
    this.c.drawImage(this.image, 0, 0);
    this.c.restore();
  }

  this.getMaximumMask = function() {
    if (this.image == null) {
      return null;
    }
    if (this.areaWidth() / this.areaHeight() > TARGET_RATIO) {
      let width = this.areaHeight() * TARGET_RATIO;
      let x = (this.areaWidth() - width) / 2;
      return new Mask(x, 0, width);
    } else {
      let y = (this.areaHeight() - this.areaWidth() / TARGET_RATIO) / 2;
      return new Mask(0, y, this.areaWidth());
    }
  }

  this.setMask = function(mask) {
    this.mask = mask;
    this.handles = this.getHandles(mask);
  }

  this.resetMask = function() {
    if (this.image == null) {
      return;
    }
    this.setMask(this.getMaximumMask(this.image));
    this.draw();
  }

  this.drawMask = function() {
    this.c.fillStyle = 'rgba(64, 64, 64, 0.5)';
    this.c.beginPath();
    this.mask.addPath(this.c);
    this.c.fill();
  }

  this.getHandles = function(mask) {
    return [
        new Handle(mask.x, mask.y, Elements.NW_HANDLE),
        new Handle(mask.x + mask.width, mask.y, Elements.NE_HANDLE),
        new Handle(
            mask.x + mask.width, mask.y + mask.height(), Elements.SE_HANDLE),
        new Handle(mask.x, mask.y + mask.height(), Elements.SW_HANDLE),
    ];
  }

  this.drawHandles = function() {
    this.c.fillStyle = 'rgb(64, 64, 64)';
    this.c.beginPath();
    for (i in this.handles) {
      this.handles[i].addPath(this.c);
    }
    this.c.fill();
  }

  this.draw = function() {
    this.drawImage();
    this.drawMask();
    this.drawHandles();
  }

  this.render = function() {
    const scaledMask = new Mask(
        this.mask.x / this.imageScale,
        this.mask.y / this.imageScale,
        this.mask.width / this.imageScale);
    if (scaledMask.width >= TARGET_WIDTH) {
      this.renderCanvas.width = TARGET_WIDTH;
      this.renderCanvas.height = TARGET_HEIGHT;
    } else {
      this.renderCanvas.width = scaledMask.width;
      this.renderCanvas.height = scaledMask.height();
    }
    const renderC = this.renderCanvas.getContext('2d');
    renderC.setTransform(1, 0, 0, 1, 0, 0);
    renderC.translate(-1 * scaledMask.x, -1 * scaledMask.y);
    const renderScale = this.renderCanvas.width / scaledMask.width;
    renderC.scale(renderScale, renderScale);
    renderC.drawImage(this.image, 0, 0);
    console.log(this.renderCanvas.toDataURL());
  }

  this.pick = function(x, y) {
    elements = this.handles.concat(this.mask);
    for (i in elements) {
      this.c.beginPath();
      elements[i].addPath(this.c);
      if (this.c.isPointInPath(x, y)) {
        return elements[i].element;
      }
    }
    return Elements.NONE;
  }

  this.pickFromEvent = function(e) {
    let x = e.clientX - this.canvas.getBoundingClientRect().left;
    let y = e.clientY - this.canvas.getBoundingClientRect().top;
    return this.pick(x, y);
  }

  this.canvas.addEventListener('mousedown', e => {
    if (this.mask == null) {
      return;
    }
    this.draggingElement = this.pickFromEvent(e);
  });

  this.canvas.addEventListener('mouseup', e => {
    this.draggingElement = Elements.NONE;
  });

  this.canvas.addEventListener('mouseleave', e => {
    this.draggingElement = Elements.NONE;
  });

  this.updateMask = function(dx, dy, dw) {
    if (this.mask == null) {
      return;
    }
    let x = this.mask.x + dx;
    let y = this.mask.y + dy;
    let width = this.mask.width + dw;

    if (x < 0) {
      width = this.mask.width;
      x = 0;
    }
    if (y < 0) {
      width = this.mask.width;
      y = 0;
    }
    if (x + width > this.areaWidth()) {
      width = this.mask.width;
      x = this.areaWidth() - width;
    }
    if (y + width / TARGET_RATIO > this.areaHeight()) {
      width = this.mask.width;
      y = this.areaHeight() - (width / TARGET_RATIO);
    }

    this.setMask(new Mask(x, y, width));
    this.draw();
  }

  this.canvas.addEventListener('mousemove', e => {
    if (this.mask == null) {
      return;
    }
    switch (this.draggingElement) {
      case Elements.NONE:
        let element = this.pickFromEvent(e);
        this.canvas.style.cursor = this.CURSOR_MAP.get(element);
        break;
      case Elements.MASK:
        this.updateMask(e.movementX, e.movementY, 0);
        break;
      case Elements.NW_HANDLE:
        {
          const dw = -1 * e.movementX;
          const dy = -1 * dw / TARGET_RATIO;
          this.updateMask(e.movementX, dy, dw);
        }
        break;
      case Elements.NE_HANDLE:
        {
          const dw = e.movementX;
          const dy = -1 * dw / TARGET_RATIO;
          this.updateMask(0, dy, dw);
        }
        break;
      case Elements.SE_HANDLE:
        this.updateMask(0, 0, e.movementX);
        break;
      case Elements.SW_HANDLE:
        this.updateMask(e.movementX, 0, -1 * e.movementX);
        break;
    }
  });
}

// Main

const container = document.querySelector('#cropper');
const canvas = document.createElement('canvas');
canvas.width = container.clientWidth;
container.appendChild(canvas);
const renderCanvas = document.createElement('canvas');
renderCanvas.style.display = 'none';
container.appendChild(renderCanvas);
const cropper = new Cropper(canvas, renderCanvas);

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
  cropper.render();
});
