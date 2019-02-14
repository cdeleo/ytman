(function (global, factory) {
  global.ThumbnailCreator = factory();
}(this, (function() {

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
    this.fileInput = React.createRef();
  }
  
  render() {
    let imageComponent;
    if (this.props.data.image) {
      imageComponent = e(ImageCropper, {
        ref: this.props.imageCropper,
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
            onClick: e => this.props.imageCropper.current.resetMask()}, 'reset')
      ),
      e(StyledTextField, {
        label: 'name',
        fullWidth: true,
        value: this.props.data.name,
        onChange: e => this.props.onChange({name: e.target.value}),
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
    if (this.props.data.nameLoading) {
      return {endAdornment: e(InputAdornment, {position: 'end'},
        e(CircularProgress, {color: 'secondary', size: 20})
      )};
    } else {
      return {};
    }
  }
  
  handleMidChange(mid) {
    if (/^[0-9]*$/.test(mid)) {
      this.props.onChange({mid: mid});
    }
  }
  
  handleMidBlur(mid) {
    if (!mid) {
      return;
    }
    this.props.onChange({nameLoading: true});
    lookupCard(mid).then(data => {
      this.props.onChange({name: data.card.name, nameLoading: false});
    });
  }
  
  handleImageChange(e) {
    if (e.target.files.length === 0) {
      this.props.onChange({image: null});
      return;
    }
    const reader = new FileReader();
    reader.onload = e => {
      const image = new Image();
      image.addEventListener('load', () => {
        this.props.onChange({image: image});
      });
      image.src = e.target.result;
    };
    reader.readAsDataURL(e.target.files[0]);
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
            onChange: (_, value) => this.props.onChange({activeType: value})},
          e(Tab, {value: 'new', label: 'New image'}),
          e(Tab, {value: 'existing', label: 'Existing image'})
        ),
        this.getPanel(
          'new', NewImagePanel, {imageCropper: this.props.imageCropper}),
        this.getPanel('existing', ExistingImagePanel)
      )
    );
  }
  
  getPanel(type, cls, extraProps={}) {
    const style = this.props.data.activeType == type ? {} : {display: 'none'};
    const props = {
      data: this.props.data[type],
      onChange: update => {
        const parentUpdate = {};
        parentUpdate[type] = Object.assign(this.props.data[type], update);
        this.props.onChange(parentUpdate);
      },
    };
    return e('div', {style: style}, e(cls, Object.assign(extraProps, props)));
  }
}

function MainContent(props) {
  return e('div', null,
    e(StyledMetadataCard, {
      title: props.title,
      subtitle: props.subtitle
    }),
    e(ImageCard, {
      data: props.data.image,
      imageCropper: props.imageCropper,
      onChange: update => props.onChange(
        {image: Object.assign(props.data.image, update)}),
    }),
    e(StyledDoneFab, {
        color: 'secondary',
        disabled: !props.isDoneEnabled,
        onClick: e => props.onDone()},
      e('i', {className: 'material-icons'}, 'done')
    )
  );
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
      data: {
        image: {
          activeType: 'new',
          'new': {
            image: null,
            name: '',
            nameLoading: false,
            mid: '',
          },
          existing: {},
        },
      }
    };
    this.imageCropper = React.createRef();
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
        isDoneEnabled: this.getIsDoneEnabled(),
        imageCropper: this.imageCropper,
        onDone: () => this.handleDone(),
        onChange: update =>
          this.setState(
            {data: Object.assign(this.state.data, update)}),
      });
    }
    return e(MuiThemeProvider, {theme: theme},
      e(CssBaseline),
      e(MainAppBar),
      content
    );
  }
  
  getIsDoneEnabled() {
    switch (this.state.data.image.activeType) {
      case 'new':
        if (!this.state.data.image.new.image) {
          return false;
        }
        if (!this.state.data.image.new.name) {
          return false;
        }
        return true;
      case 'existing':
        return false;
      default:
        return false;
    }
  }
  
  handleDone() {
    const output = {
      title: this.state.title,
      subtitle: this.state.subtitle,
      onUpdate: update => this.handleWorkingUpdate(update)
    };
    switch (this.state.data.image.activeType) {
      case 'new':
        output.image = {
          type: 'new',
          data: this.imageCropper.current.renderImage(),
          name: this.state.data.image.new.name,
          mid: this.state.data.image.new.mid,
        };
        break;
      default:
        output.image = {};
    }
    this.setState({working: true, workingMessage: 'Processing...'});
    this.props.onDone(output);
  }
  
  handleWorkingUpdate(update) {
    this.setState({workingMessage: update.message});
  }
}

return ThumbnailCreator;
})));