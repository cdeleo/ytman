(function (global, factory) {
  global.ImageCropper = factory();
}(this, (function() {
  
const e = React.createElement;

const Elements = Object.freeze({
  NONE: 'none',
  MASK: 'mask',
  NW_HANDLE: 'nwHandle',
  NE_HANDLE: 'neHandle',
  SE_HANDLE: 'seHandle',
  SW_HANDLE: 'swHandle',
});

const HANDLE_SIZE = 10;
const PADDING = 10;
const TARGET_WIDTH = 1280;
const TARGET_HEIGHT = 720;
const TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT;

const CURSOR_MAP = new Map([
  [Elements.NONE, 'default'],
  [Elements.MASK, 'move'],
  [Elements.NW_HANDLE, 'nw-resize'],
  [Elements.NE_HANDLE, 'ne-resize'],
  [Elements.SE_HANDLE, 'se-resize'],
  [Elements.SW_HANDLE, 'sw-resize'],
]);

class Handle {
  constructor(x, y, element) {
    this.x = x;
    this.y = y;
    this.element = element;
  }

  addPath(c) {
    c.rect(
      this.x - HANDLE_SIZE / 2,
      this.y - HANDLE_SIZE / 2,
      HANDLE_SIZE,
      HANDLE_SIZE);
  }
}

class Mask {
  constructor(x, y, width) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.element = Elements.MASK;
  }

  get height() {
    return this.width / TARGET_RATIO;
  }

  addPath(c) {
    c.rect(this.x, this.y, this.width, this.height);
  }
}

class ImageCropper extends React.Component {
  constructor(props) {
    super(props);
    this.state = {mask: null, draggingElement: Elements.NONE};
    this.canvas = React.createRef();
    this.renderCanvas = React.createRef();
  }
  
  render() {
    const height = this.props.image ? this.imageScale * this.props.image.height + 2 * PADDING : 0;
    return e('div', null,
      e('canvas', {
        ref: this.canvas,
        width: this.props.width,
        height: height,
        onMouseDown: e => this.handleMouseDown(e),
        onMouseUp: e => this.handleMouseUp(e),
        onMouseLeave: e => this.handleMouseLeave(e),
        onMouseMove: e => this.handleMouseMove(e),
      }, null),
      e('canvas', {ref: this.renderCanvas, style: {display: 'none'}}, null)
    );
  }
  
  componentDidMount() {
    this.c = this.canvas.current.getContext('2d');
  }
  
  componentDidUpdate() {
    if (this.props.image && !this.state.mask) {
      this.setState({mask: this.getMaximumMask()});
    }
    this.c.setTransform(1, 0, 0, 1, PADDING, PADDING);
    this.draw();
  }
  
  renderImage() {
    if (!this.props.image) {
      return null;
    }
    const scaledMask = new Mask(
      this.state.mask.x / this.imageScale,
      this.state.mask.y / this.imageScale,
      this.state.mask.width / this.imageScale);
    if (scaledMask.width >= TARGET_WIDTH) {
      this.renderCanvas.current.width = TARGET_WIDTH;
      this.renderCanvas.current.height = TARGET_HEIGHT;
    } else {
      this.renderCanvas.current.width = scaledMask.width;
      this.renderCanvas.current.height = scaledMask.height;
    }
    const renderC = this.renderCanvas.current.getContext('2d');
    renderC.setTransform(1, 0, 0, 1, 0, 0);
    renderC.translate(-1 * scaledMask.x, -1 * scaledMask.y);
    const renderScale = this.renderCanvas.current.width / scaledMask.width;
    renderC.scale(renderScale, renderScale);
    renderC.drawImage(this.props.image, 0, 0);
    return this.renderCanvas.current.toDataURL();
  }
  
  resetMask() {
    this.setState({mask: this.getMaximumMask()});
  }
  
  draw() {
    if (this.props.image && this.state.mask) {
      this.drawImage();
      this.drawMask();
      this.drawHandles();
    }
  }
  
  drawImage() {
    this.c.save();
    this.c.clearRect(
      -1 * PADDING,
      -1 * PADDING,
      this.canvas.current.width,
      this.canvas.current.height);
    this.c.scale(this.imageScale, this.imageScale);
    this.c.drawImage(this.props.image, 0, 0);
    this.c.restore();
  }

  drawMask() {
    this.c.fillStyle = 'rgba(64, 64, 64, 0.5)';
    this.c.beginPath();
    this.state.mask.addPath(this.c);
    this.c.fill();
  }

  drawHandles() {
    this.c.fillStyle = 'rgb(64, 64, 64)';
    this.c.beginPath();
    this.handles.forEach(handle => handle.addPath(this.c));
    this.c.fill();
  }
  
  updateMask(dx, dy, dw) {
    if (!this.state.mask) {
      return;
    }
    let x = this.state.mask.x + dx;
    let y = this.state.mask.y + dy;
    let width = this.state.mask.width + dw;

    if (x < 0) {
      width = this.state.mask.width;
      x = 0;
      y = this.state.mask.y;
    }
    if (y < 0) {
      width = this.state.mask.width;
      y = 0;
    }
    if (x + width > this.areaWidth) {
      width = this.state.mask.width;
      x = this.areaWidth - width;
      y = this.state.mask.y;
    }
    if (y + width / TARGET_RATIO > this.areaHeight) {
      width = this.state.mask.width;
      y = this.areaHeight - (width / TARGET_RATIO);
    }

    this.setState({mask: new Mask(x, y, width)});
  }
  
  pickFromEvent(e) {
    const x = e.clientX - this.canvas.current.getBoundingClientRect().left;
    const y = e.clientY - this.canvas.current.getBoundingClientRect().top;
    return this.pick(x, y);
  }
  
  pick(x, y) {
    for (const element of this.handles.concat(this.state.mask)) {
      this.c.beginPath();
      element.addPath(this.c);
      if (this.c.isPointInPath(x, y)) {
        return element.element;
      }
    }
    return Elements.NONE;
  }
  
  handleMouseDown(e) {
    if (!this.state.mask) {
      return;
    }
    this.setState({draggingElement: this.pickFromEvent(e)});
  }

  handleMouseUp() {
    this.setState({draggingElement: Elements.NONE});
  }

  handleMouseLeave() {
    this.setState({draggingElement: Elements.NONE});
  }
  
  handleMouseMove(e) {
    if (!this.state.mask) {
      return;
    }
    switch (this.state.draggingElement) {
      case Elements.NONE:
        const element = this.pickFromEvent(e);
        this.canvas.current.style.cursor = CURSOR_MAP.get(element);
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
  }
  
  getMaximumMask() {
    if (!this.props.image) {
      return null;
    }
    if (this.areaWidth / this.areaHeight > TARGET_RATIO) {
      let width = this.areaHeight * TARGET_RATIO;
      let x = (this.areaWidth - width) / 2;
      return new Mask(x, 0, width);
    } else {
      let y = (this.areaHeight - this.areaWidth / TARGET_RATIO) / 2;
      return new Mask(0, y, this.areaWidth);
    }
  }
  
  get areaWidth() {
    return this.canvas.current.width - 2 * PADDING;
  }

  get areaHeight() {
    return this.canvas.current.height - 2 * PADDING;
  }
  
  get handles() {
    const mask = this.state.mask;
    return [
      new Handle(mask.x, mask.y, Elements.NW_HANDLE),
      new Handle(mask.x + mask.width, mask.y, Elements.NE_HANDLE),
      new Handle(
          mask.x + mask.width, mask.y + mask.height, Elements.SE_HANDLE),
      new Handle(mask.x, mask.y + mask.height, Elements.SW_HANDLE),
    ];
  }

  get imageScale() {
    return this.props.image ? (this.props.width - 2 * PADDING) / this.props.image.width : 1;
  }
}

return ImageCropper;
})));