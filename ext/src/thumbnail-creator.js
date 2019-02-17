(function (global, factory) {
  global.ThumbnailCreator = factory();
}(this, (function() {

const BACKEND_APP_ID = 'backend-dot-youtube-manager-196811';
const MTG_IO_URL = 'https://api.magicthegathering.io/v1/';
const RATIO = 720 / 1280;
const WIDTH = 400;

const e = React.createElement;

const {
  AppBar,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  CircularProgress,
  CssBaseline,
  Fab,
  InputAdornment,
  MuiThemeProvider,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Tabs,
  TextField,
  Toolbar,
  Typography,
  createMuiTheme,
  withStyles
} = window['material-ui'];

function lookupCard(mid, needSet=false) {
  return fetch(MTG_IO_URL + 'cards/' + mid)
    .then(cardResponse => cardResponse.json())
    .then(cardData => {
      if (needSet) {
        return fetch(MTG_IO_URL + 'sets/' + cardData.card.set)
          .then(setResponse => setResponse.json())
          .then(setData => {
            return {
              card: cardData.card,
              set: setData.set,
            };
          });
      } else {
        return {card: cardData.card};
      }
    });
}

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

function createImage(data, name, mid) {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({interactive: true}, token => {
      const params = new URLSearchParams({
        data: data,
        name: name,
      });
      if (mid) {
        params.metadata = [{key: 'mid', value: parseInt(mid)}];
      }
      fetch(
          apiUrl(BACKEND_APP_ID, 'ytman', 'v1', 'images/create'),
          {
            method: 'POST',
            headers: {Authorization: 'Bearer ' + token},
            body: params,
          })
        .then(res => res.json())
        .then(data => resolve(data.image))
        .catch(e => reject(e));
    });
  });
}

function getDescription(mid) {
  if (mid) {
    return lookupCard(mid, needSet=true)
      .then(data => {
        const name = data.card.name;
        const artist = data.card.artist;
        const year = data.set.releaseDate.substring(0, 4);
        const company = (
            'Wizards of the Coast LLC, a subsidiary of Hasbro, Inc.');
        return (
          `Thumbnail from ${name} by ${artist}\n` +
          `\u00A9 ${year} ${company}`
        );
      });
  } else {
    return new Promise(resolve => resolve(null));
  }
}

const theme = createMuiTheme({
  palette: {
    type: 'light',
    primary: {
      main: '#757575',
    },
    secondary: {
      main: '#b71c1c',
    },
  },
});

const StyledCard = withStyles(theme => ({
  root: {
    margin: theme.spacing.unit * 2,
  }
}))(Card);

const StyledDoneFab = withStyles(theme => ({
  root: {
    position: 'fixed',
    bottom: theme.spacing.unit * 2,
    right: theme.spacing.unit * 2,
  }
}))(Fab);

const StyledTextField = withStyles(theme => ({
  root: {
    marginLeft: theme.spacing.unit,
    marginRight: theme.spacing.unit,
  }
}))(TextField);

function MainAppBar(props) {
  return e(AppBar, {position: 'sticky'},
    e(Toolbar, null,
      e(Typography, {variant: 'h6', color: 'inherit'}, 'Generate thumbnail')
    )
  );
}

function MetadataCard(props) {
  const data = [
    {key: 'title', label: 'title', value: props.title},
    {key: 'subtitle', label: 'subtitle', value: props.subtitle},
  ];
  return e(StyledCard, null,
    e(CardContent, null,
      e(Table, null,
        e(TableBody, null,
          data.map(row =>
            e(TableRow, {key: row.key},
              e(TableCell, {
                  className: props.classes.cell,
                  style: {width: 100}},
                e(Typography, {
                    className: props.classes.label, variant: 'subtitle1'},
                  row.label)
              ),
              e(TableCell, {className: props.classes.cell},
                e(Typography, {variant: 'subtitle1'}, row.value)
              )
            )
          )
        )
      )
    )
  );
}

const StyledMetadataCard = withStyles(theme => ({
  cell: {
    ':last-of-type > &': {
      borderStyle: 'none'
    }
  },
  label: {
    color: theme.palette.text.secondary,
  }
}))(MetadataCard);

function ImagePlaceholder(props) {
  const height = Math.round(props.width * RATIO);
  return e('div', {
    className: props.classes.root,
    style: {width: props.width, height: height}});
}

const StyledImagePlaceholder = withStyles(theme => ({
  root: {
    marginTop: theme.spacing.unit,
    marginBottom: theme.spacing.unit,
    backgroundColor: theme.palette.grey[300],
  }
}))(ImagePlaceholder);

class NewImagePanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {loadingName: false};
    this.imageCropper = React.createRef();
    this.fileInput = React.createRef();
  }
  
  static get defaultProps() {
    return {
      data: {
        image: null,
        name: '',
        mid: '',
      }
    };
  }
  
  render() {
    let imageComponent;
    if (this.props.data.image) {
      imageComponent = e(ImageCropper, {
        ref: this.imageCropper,
        image: this.props.data.image,
        width: WIDTH
      });
    } else {
      imageComponent = e(StyledImagePlaceholder, {width: WIDTH});
    }
    return e('div', null,
      imageComponent,
      e('div', null,
        e(Button, {
            onClick: e => this.fileInput.current.click()}, 'select'),
        e(Button, {
            onClick: e => {
              if (this.imageCropper.current) {
                this.imageCropper.current.resetMask();
              }
            }}, 'reset')
      ),
      e(StyledTextField, {
        label: 'name',
        fullWidth: true,
        value: this.props.data.name,
        onChange: e => this.handleChange({name: e.target.value}),
        InputProps: this.getNameInputProps(),
      }),
      e(StyledTextField, {
        label: 'multiverse id',
        fullWidth: true,
        value: this.props.data.mid,
        onChange: e => this.handleMidChange(e.target.value),
        onBlur: e => this.handleMidBlur(e.target.value),
      }),
      e('input', {
        ref: this.fileInput,
        style: {display: 'none'},
        type: 'file',
        accept: 'image/*',
        onChange: e => this.handleImageChange(e),
      })
    );
  }
  
  getNameInputProps() {
    if (this.state.loadingName) {
      return {endAdornment: e(InputAdornment, {position: 'end'},
        e(CircularProgress, {color: 'secondary', size: 20})
      )};
    } else {
      return {};
    }
  }
  
  handleChange(update) {
    const newData = Object.assign(this.props.data, update);
    this.props.onChange(
      {
        data: newData,
        isValid: this.getIsValid(newData),
        getBgKey: () => this.getBgKey(),
        getDescription: () => getDescription(this.props.data.mid),
      });
  }
  
  getIsValid(data) {
    if (!data.image) {
      return false;
    }
    if (!data.name) {
      return false;
    }
    return true;
  }
  
  handleMidChange(mid) {
    if (/^[0-9]*$/.test(mid)) {
      this.handleChange({mid: mid});
    }
  }
  
  handleMidBlur(mid) {
    if (!mid) {
      return;
    }
    this.setState({loadingName: true});
    lookupCard(mid).then(data => {
      this.handleChange({name: data.card.name});
      this.setState({loadingName: false});
    });
  }
  
  handleImageChange(e) {
    if (e.target.files.length === 0) {
      this.handleChange({image: null});
      return;
    }
    const reader = new FileReader();
    reader.onload = e => {
      const image = new Image();
      image.addEventListener('load', () => {
        this.handleChange({image: image});
      });
      image.src = e.target.result;
    };
    reader.readAsDataURL(e.target.files[0]);
  }
  
  getBgKey() {
    return createImage(
        this.imageCropper.current.renderImage(),
        this.props.data.name,
        this.props.data.mid)
      .then(image => image.key);
  }
}

function ExistingImagePanel(props) {
  return e(StyledImagePlaceholder, {width: WIDTH});
}

class ImageCard extends React.Component {
  render() {
    return e(StyledCard, null,
      e(CardContent, null,
        e(Tabs, {
            variant: 'fullWidth',
            value: this.props.data.activeType,
            onChange: (_, value) => this.handleChange({activeType: value})},
          e(Tab, {value: 'new', label: 'New image'}),
          e(Tab, {value: 'existing', label: 'Existing image'})
        ),
        this.getPanel('new', NewImagePanel),
        this.getPanel('existing', ExistingImagePanel)
      )
    );
  }
  
  static get defaultProps() {
    return {
      data: {
        activeType: 'new',
        'new': {},
        existing: {},
      }
    };
  }
  
  getPanel(type, cls) {
    const style = this.props.data.activeType == type ? {} : {display: 'none'};
    const props = {
      data: this.props.data[type].data,
      onChange: value => {
        const update = {};
        update[type] = value;
        this.handleChange(update);
      },
    };
    return e('div', {style: style}, e(cls, props));
  }
  
  handleChange(update) {
    const newData = Object.assign(this.props.data, update);
    const activeImageData = newData[newData.activeType] || {isValid: false};
    this.props.onChange({
      data: newData,
      isValid: activeImageData.isValid,
      getBgKey: activeImageData.getBgKey,
      getDescription: activeImageData.getDescription,
    });
  }
}

class MainContent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {image: {isValid: false}};
  }
  
  render() {
    return e('div', null,
      e(StyledMetadataCard, {
        title: this.props.title,
        subtitle: this.props.subtitle
      }),
      e(ImageCard, {
        data: this.state.image.data,
        onChange: value => this.setState({image: value})
      }),
      e(StyledDoneFab, {
          color: 'secondary',
          disabled: !this.state.image.isValid,
          onClick: e => this.props.onDone({
            getBgKey: this.state.image.getBgKey,
            getDescription: this.state.image.getDescription,
          })},
        e('i', {className: 'material-icons'}, 'done')
      )
    );
  }
}

function WorkingContent(props) {
  const containerStyle = {
    width: WIDTH,
    height: Math.round(WIDTH * RATIO),
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
  };
  return e('div', {style: containerStyle},
    e('div', null,
      e(CircularProgress, {color: 'secondary', style: {margin: 16}})
    ),
    e('div', null,
      e(Typography, null, props.message)
    )
  );
}

class ThumbnailCreator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      working: false,
      title: null,
      subtitle: null,
      workingMessage: '',
    };
  }
  
  componentDidMount() {
    if (chrome.runtime) {
      chrome.runtime.onMessage.addListener(
        request => {
          switch (request.type) {
            case 'LOAD_DATA':
              this.setState(request.data);
              break;
          }
        }
      );
    } else {
      this.setState({title: 'title', subtitle: 'subtitle'});
    }
  }
  
  render() {
    let content;
    if (this.state.working) {
      content = e(WorkingContent, {message: this.state.workingMessage});
    } else {
      content = e(MainContent, {
        data: this.state.data,
        title: this.state.title,
        subtitle: this.state.subtitle,
        onDone: output => this.handleDone(output),
      });
    }
    return e(MuiThemeProvider, {theme: theme},
      e(CssBaseline),
      e(MainAppBar),
      content
    );
  }
  
  handleDone(data) {
    this.setState({working: true, workingMessage: 'Processing...'});
    this.props.onDone({
      title: this.state.title,
      subtitle: this.state.subtitle,
      getBgKey: data.getBgKey,
      getDescription: data.getDescription,
      onUpdate: update => this.setState({workingMessage: update.message}),
    });
  }
}

return ThumbnailCreator;
})));