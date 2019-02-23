(function (global, factory) {
  global.SvgRenderer = factory();
}(this, (function() {
  
TAGS_TO_IGNORE = new Set(['svg', 'defs']);

function value(x) {
  if (x.baseVal) {
    if (x.baseVal.length) {
      return x.baseVal[0].value;
    } else {
      return x.baseVal.value;
    }
  } else {
    return x;
  }
}

function setFont(c, state) {
  const fontTokens = [];
  if (state.fontStyle) {
    fontTokens.push(state.fontStyle);
  }
  if (state.fontVariant) {
    fontTokens.push(state.fontVariant);
  }
  if (state.fontWeight) {
    fontTokens.push(state.fontWeight);
  }
  if (state.fontSize) {
    if (state.lineHeight) {
      fontTokens.push(state.fontSize + '/' + state.lineHeight);
    } else {
      fontTokens.push(state.fontSize);
    }
  }
  if (state.fontFamily) {
    fontTokens.push(state.fontFamily);
  }
  c.font = fontTokens.join(' ');
}

class StateStack {
  constructor(initialState={}) {
    this._stack = [initialState];
  }
  
  save() {
    this._stack.push(Object.assign({}, this.current()));
  }
  
  restore() {
    this._stack.pop();
  }
  
  current() {
    return this._stack[this._stack.length - 1];
  }
}
  
class SvgRenderer {
  constructor(parser, svgString, fontMap={}) {
    this.parser = parser;
    this.svgString = svgString;
    this.fontMap = fontMap;
  }
  
  render(c, valueMap) {
    const svg = this.parser.parseFromString(this.svgString, 'image/svg+xml');
    const state = new StateStack();
    const operations = [];
    this._traverse(svg.documentElement, state, operations);
    Promise.all(operations).then(resolvedOperations => {
      for (const op of resolvedOperations) {
        op(c, valueMap);
      }
    });
  }
  
  _traverse(root, state, operations) {
    state.save();
    this._parseState(state.current(), root);
    const currentState = Object.assign({}, state.current());
    operations.push(c => {
      c.save();
      this._applyState(c, currentState);
    });
    const r = this._innerRender(root, currentState);
    if (r.operation) {
      operations.push(r.operation);
    }
    if (r.processChildren) {
      for (const child of root.children) {
        this._traverse(child, state, operations);
      }
    }
    operations.push(c => c.restore());
    state.restore();
  }
  
  _parseState(state, node) {
    if (node.style) {
      for (const prop of node.style) {
        switch (prop) {
          case 'fill':
            state.fillStyle = node.style[prop];
            break;
          case 'font-family':
            state.fontFamily = node.style[prop];
            break;
          case 'font-size':
            state.fontSize = node.style[prop];
            break;
          case 'font-style':
            state.fontStyle = node.style[prop];
            break;
          case 'font-variant':
            state.fontVariant = node.style[prop];
            break;
          case 'font-weight':
            state.fontWeight = node.style[prop];
            break;
          case 'line-height':
            state.lineHeight = node.style[prop];
            break;
          case 'stroke':
            const stroke = node.style[prop];
            state.strokeStyle = stroke == 'none' ? '#00000000' : stroke;
            break;
          case 'stroke-width':
            state.lineWidth = node.style[prop];
            break;
        }
      }
    }
    if (node.transform) {
      state.transform = node.transform.baseVal;
    }
  }
  
  _applyState(c, state) {
    if (state.fillStyle) {
      c.fillStyle = state.fillStyle;
    }
    if (state.strokeStyle) {
      c.strokeStyle = state.strokeStyle;
    }
    if (state.lineWidth) {
      c.lineWidth = state.lineWidth;
    }
    setFont(c, state);
    if (state.transform) {
      for (let i = 0; i < state.transform.length; i++) {
        const t = state.transform[i].matrix;
        c.transform(t.a, t.b, t.c, t.d, t.e, t.f);
      }
    }
  }
  
  _loadFontFamily(fontFamily) {
    if (this.fontMap[fontFamily]) {
      const font = new FontFace(fontFamily, this.fontMap[fontFamily]);
      return font.load();
    } else {
      return Promise.resolve(null);
    }
  }
  
  _innerRender(node, state) {
    const handlerName = (
      '_render'
      + node.tagName[0].toUpperCase()
      + node.tagName.substring(1));
    if (this[handlerName]) {
      return this[handlerName](node, state);
    } else if (this._ignoreTag(node.tagName)) {
      return {processChildren: true};
    } else {
      console.log('Skipping ' + node.tagName);
      return {processChildren: true};
    }
  }
  
  _renderMetadata(node) {
    return {};
  }
  
  _renderG(node) {
    return {processChildren: true};
  }
  
  _renderImage(node) {
    const args = [
      value(node.x),
      value(node.y),
      value(node.width),
      value(node.height)
    ];
    return {
      operation: new Promise((resolve, reject) => {
          const image = new Image();
          image.onload = () => resolve(image);
          image.onerror = e => reject(e);
          image.src = node.href.baseVal;
        })
        .then(image => {
          return c => c.drawImage(image, ...args);
        })
        .catch(e => {
          return c => {
            console.log('Error loading image:\n' + e);
            c.fillStyle = 'red';
            c.fillRect(...args);
          };
        })
    };
  }
  
  _renderPath(node) {
    return {
      operation: Promise.resolve(c => {
        const path = new Path2D(node.getAttribute('d'));
        c.fill(path);
        c.stroke(path);
      })
    };
  }
  
  _renderRect(node) {
    return {
      operation: Promise.resolve(c => {
        const args = [
          value(node.x),
          value(node.y),
          value(node.width),
          value(node.height)
        ];
        c.fillRect(...args);
        c.strokeRect(...args);
      })
    };
  }
  
  _renderText(node, state) {
    if (node.children.length) {
      return {processChildren: true};
    } else {
      return _renderTspan(node, state);
    }
  }
  
  _renderTspan(node, state) {
    return {
      operation: this._loadFontFamily(state.fontFamily)
        .then(loadedFont => {
          if (loadedFont) {
            document.fonts.add(loadedFont);
          }
        })
        .catch(e => console.log('Error loading font:\n' + e))
        .then(() => {
          return (c, valueMap) => {
            const textContent = node.textContent.replace(
              /\{(.+?)\}/g,
              (match, key) => valueMap[key] ? valueMap[key] : match
            );
            const args = [
              textContent,
              value(node.x),
              value(node.y)
            ];
            c.fillText(...args);
            c.strokeText(...args);
          };
        })
    };
  }
  
  _ignoreTag(tagName) {
    if (tagName.startsWith('sodipodi')) {
      return true;
    }
    if (TAGS_TO_IGNORE.has(tagName)) {
      return true;
    }
    return false;
  }
  
  
}
  
return SvgRenderer;
})));