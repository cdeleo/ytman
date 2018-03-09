// Cropper

const HANDLE_SIZE = 10;
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

function getInitialMask(image) {
  if (image.width / image.height > TARGET_RATIO) {
    let width = image.height * TARGET_RATIO;
    let x = (image.width - width) / 2;
    return new Mask(x, 0, width);
  } else {
    let y = (image.height - image.width / TARGET_RATIO) / 2;
    return new Mask(0, y, image.width);
  }
}

function Handle(x, y, element) {
  this.x = x;
  this.y = y;
  this.element = element;

  this.buildPath = function(c) {
    c.beginPath();
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

  this.buildPath = function(c) {
    c.beginPath();
    c.rect(this.x, this.y, this.width, this.height());
  }
}

function Cropper(canvas) {
  
  this.CURSOR_MAP = new Map([
      [Elements.NONE, 'default'],
      [Elements.MASK, 'move'],
      [Elements.NW_HANDLE, 'nw-resize'],
      [Elements.NE_HANDLE, 'ne-resize'],
      [Elements.SE_HANDLE, 'se-resize'],
      [Elements.SW_HANDLE, 'sw-resize'],
  ]);

  this.canvas = canvas;
  this.c = canvas.getContext('2d');
  this.image = null;
  this.imageScale = null;
  this.mask = null;
  this.handles = null;

  this.setImage = function(image) {
    this.image = image;
    this.imageScale = this.canvas.width / image.width;
    this.canvas.height = this.imageScale * image.height;
    this.setMask(new Mask(100, 100, 100));
    this.draw();
  }

  this.drawImage = function() {
    this.c.save();
    this.c.scale(this.imageScale, this.imageScale);
    this.c.drawImage(this.image, 0, 0);
    this.c.restore();
  }

  this.setMask = function(mask) {
    this.mask = mask;
    this.handles = this.getHandles(mask);
  }

  this.drawMask = function() {
    this.c.fillStyle = 'rgba(64, 64, 64, 0.5)';
    this.mask.buildPath(this.c);
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
    for (i in this.handles) {
      this.handles[i].buildPath(this.c);
      this.c.fill();
    }
  }

  this.draw = function() {
    this.drawImage();
    this.drawMask();
    this.drawHandles();
  }

  this.pick = function(x, y) {
    elements = this.handles.concat(this.mask);
    for (i in elements) {
      elements[i].buildPath(this.c);
      if (this.c.isPointInPath(x, y)) {
        return elements[i].element;
      }
    }
    return Elements.NONE;
  }

  this.canvas.addEventListener('mousemove', e => {
    if (this.mask == null) {
      return;
    }
    let x = e.clientX - this.canvas.getBoundingClientRect().left;
    let y = e.clientY - this.canvas.getBoundingClientRect().top;
    let element = this.pick(x, y);
    this.canvas.style.cursor = this.CURSOR_MAP.get(element);
  });
}

// Main

const container = document.querySelector('div');
const canvas = document.querySelector('canvas');
canvas.width = container.clientWidth;
const cropper = new Cropper(canvas);

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
