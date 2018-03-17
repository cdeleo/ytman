function Cropper(canvas, renderCanvas) {

  // Public

  this.setImage = function(image) {
    this._image = image;
    this._imageScale = (this._canvas.width - 2 * _PADDING) / image.width;
    this._canvas.height = this._imageScale * image.height + 2 * _PADDING;
    this._c.setTransform(1, 0, 0, 1, _PADDING, _PADDING);
    this.resetMask();
  }

  this.hasImage = function() {
    return this._image != null;
  }

  this.resetMask = function() {
    if (this._image == null) {
      return;
    }
    this._setMask(this._getMaximumMask(this._image));
    this._draw();
  }

  this.render = function() {
    if (this._image == null) {
      return null;
    }
    const scaledMask = new _Mask(
        this._mask.x / this._imageScale,
        this._mask.y / this._imageScale,
        this._mask.width / this._imageScale);
    if (scaledMask.width >= _TARGET_WIDTH) {
      this._renderCanvas.width = _TARGET_WIDTH;
      this._renderCanvas.height = _TARGET_HEIGHT;
    } else {
      this._renderCanvas.width = scaledMask.width;
      this._renderCanvas.height = scaledMask.height();
    }
    const renderC = this._renderCanvas.getContext('2d');
    renderC.setTransform(1, 0, 0, 1, 0, 0);
    renderC.translate(-1 * scaledMask.x, -1 * scaledMask.y);
    const renderScale = this._renderCanvas.width / scaledMask.width;
    renderC.scale(renderScale, renderScale);
    renderC.drawImage(this._image, 0, 0);
    return this._renderCanvas.toDataURL();
  }

  // Private

  const _HANDLE_SIZE = 10;
  const _PADDING = 10;
  const _TARGET_WIDTH = 1280;
  const _TARGET_HEIGHT = 720;
  const _TARGET_RATIO = _TARGET_WIDTH / _TARGET_HEIGHT;

  const _Elements = Object.freeze({
      NONE: 'none',
      MASK: 'mask',
      NW_HANDLE: 'nwHandle',
      NE_HANDLE: 'neHandle',
      SE_HANDLE: 'seHandle',
      SW_HANDLE: 'swHandle',
  });

  function _Handle(x, y, element) {
    this.x = x;
    this.y = y;
    this.element = element;

    this.addPath = function(c) {
      c.rect(
          this.x - _HANDLE_SIZE / 2,
          this.y - _HANDLE_SIZE / 2,
          _HANDLE_SIZE,
          _HANDLE_SIZE);
    }
  }

  function _Mask(x, y, width) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.element = _Elements.MASK;

    this.height = function() {
      return this.width / _TARGET_RATIO;
    }

    this.addPath = function(c) {
      c.rect(this.x, this.y, this.width, this.height());
    }
  }
    
  this._CURSOR_MAP = new Map([
      [_Elements.NONE, 'default'],
      [_Elements.MASK, 'move'],
      [_Elements.NW_HANDLE, 'nw-resize'],
      [_Elements.NE_HANDLE, 'ne-resize'],
      [_Elements.SE_HANDLE, 'se-resize'],
      [_Elements.SW_HANDLE, 'sw-resize'],
  ]);

  this._canvas = canvas;
  this._renderCanvas = renderCanvas;
  this._c = canvas.getContext('2d');
  this._image = null;
  this._imageScale = null;
  this._mask = null;
  this._handles = null;
  this._draggingElement = _Elements.NONE;

  this._areaWidth = function() {
    return this._canvas.width - 2 * _PADDING;
  }

  this._areaHeight = function() {
    return this._canvas.height - 2 * _PADDING;
  }

  this._drawImage = function() {
    this._c.save();
    this._c.clearRect(
        -1 * _PADDING, -1 * _PADDING, this._canvas.width, this._canvas.height);
    this._c.scale(this._imageScale, this._imageScale);
    this._c.drawImage(this._image, 0, 0);
    this._c.restore();
  }

  this._getMaximumMask = function() {
    if (this._image == null) {
      return null;
    }
    if (this._areaWidth() / this._areaHeight() > _TARGET_RATIO) {
      let width = this._areaHeight() * _TARGET_RATIO;
      let x = (this._areaWidth() - width) / 2;
      return new _Mask(x, 0, width);
    } else {
      let y = (this._areaHeight() - this._areaWidth() / _TARGET_RATIO) / 2;
      return new _Mask(0, y, this._areaWidth());
    }
  }

  this._setMask = function(mask) {
    this._mask = mask;
    this._handles = this._getHandles(mask);
  }

  this._drawMask = function() {
    this._c.fillStyle = 'rgba(64, 64, 64, 0.5)';
    this._c.beginPath();
    this._mask.addPath(this._c);
    this._c.fill();
  }

  this._getHandles = function(mask) {
    return [
        new _Handle(mask.x, mask.y, _Elements.NW_HANDLE),
        new _Handle(mask.x + mask.width, mask.y, _Elements.NE_HANDLE),
        new _Handle(
            mask.x + mask.width, mask.y + mask.height(), _Elements.SE_HANDLE),
        new _Handle(mask.x, mask.y + mask.height(), _Elements.SW_HANDLE),
    ];
  }

  this._drawHandles = function() {
    this._c.fillStyle = 'rgb(64, 64, 64)';
    this._c.beginPath();
    for (i in this._handles) {
      this._handles[i].addPath(this._c);
    }
    this._c.fill();
  }

  this._draw = function() {
    this._drawImage();
    this._drawMask();
    this._drawHandles();
  }

  this._pick = function(x, y) {
    elements = this._handles.concat(this._mask);
    for (i in elements) {
      this._c.beginPath();
      elements[i].addPath(this._c);
      if (this._c.isPointInPath(x, y)) {
        return elements[i].element;
      }
    }
    return _Elements.NONE;
  }

  this._pickFromEvent = function(e) {
    let x = e.clientX - this._canvas.getBoundingClientRect().left;
    let y = e.clientY - this._canvas.getBoundingClientRect().top;
    return this._pick(x, y);
  }

  this._canvas.addEventListener('mousedown', e => {
    if (this._mask == null) {
      return;
    }
    this._draggingElement = this._pickFromEvent(e);
  });

  this._canvas.addEventListener('mouseup', e => {
    this._draggingElement = _Elements.NONE;
  });

  this._canvas.addEventListener('mouseleave', e => {
    this._draggingElement = _Elements.NONE;
  });

  this._updateMask = function(dx, dy, dw) {
    if (this._mask == null) {
      return;
    }
    let x = this._mask.x + dx;
    let y = this._mask.y + dy;
    let width = this._mask.width + dw;

    if (x < 0) {
      width = this._mask.width;
      x = 0;
    }
    if (y < 0) {
      width = this._mask.width;
      y = 0;
    }
    if (x + width > this._areaWidth()) {
      width = this._mask.width;
      x = this._areaWidth() - width;
    }
    if (y + width / _TARGET_RATIO > this._areaHeight()) {
      width = this._mask.width;
      y = this._areaHeight() - (width / _TARGET_RATIO);
    }

    this._setMask(new _Mask(x, y, width));
    this._draw();
  }

  this._canvas.addEventListener('mousemove', e => {
    if (this._mask == null) {
      return;
    }
    switch (this._draggingElement) {
      case _Elements.NONE:
        let element = this._pickFromEvent(e);
        this._canvas.style.cursor = this._CURSOR_MAP.get(element);
        break;
      case _Elements.MASK:
        this._updateMask(e.movementX, e.movementY, 0);
        break;
      case _Elements.NW_HANDLE:
        {
          const dw = -1 * e.movementX;
          const dy = -1 * dw / _TARGET_RATIO;
          this._updateMask(e.movementX, dy, dw);
        }
        break;
      case _Elements.NE_HANDLE:
        {
          const dw = e.movementX;
          const dy = -1 * dw / _TARGET_RATIO;
          this._updateMask(0, dy, dw);
        }
        break;
      case _Elements.SE_HANDLE:
        this._updateMask(0, 0, e.movementX);
        break;
      case _Elements.SW_HANDLE:
        this._updateMask(e.movementX, 0, -1 * e.movementX);
        break;
    }
  });
}
