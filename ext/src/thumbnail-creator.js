(function (global, factory) {
  global.ThumbnailCreator = factory();
}(this, (function() {

const APP_ID = 'backend-dot-youtube-manager-196811';
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

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
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

function visibility(visible) {
  return visible ? {} : {style: {display: 'none'}};
}

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
    this.state = {image: null};
    this.fileInput = React.createRef();
  }
  
  render() {
    let imageComponent;
    if (this.state.image) {
      imageComponent = e(ImageCropper, {
        ref: this.props.imageCropper,
        image: this.state.image,
        width: WIDTH
      });
    } else {
      imageComponent = e(StyledImagePlaceholder, {width: WIDTH});
    }
    return e('div', visibility(this.props.visible),
      imageComponent,
      e('div', null,
        e(Button, {
            onClick: e => this.fileInput.current.click()}, 'select'),
        e(Button, {
            onClick: e => this.props.imageCropper.current.resetMask()}, 'reset')
      ),
      e(StyledTextField, {label: 'name', fullWidth: true}),
      e(StyledTextField, {label: 'multiverse id', fullWidth: true}),
      e('input', {
        ref: this.fileInput,
        style: {display: 'none'},
        type: 'file',
        accept: 'image/*',
        onChange: e => this.handleImageChange(e)
      })
    );
  }
  
  handleImageChange(e) {
    if (e.target.files.length === 0) {
      this.setState({image: null});
      return;
    }
    const reader = new FileReader();
    reader.onload = e => {
      const image = new Image();
      image.addEventListener('load', () => {
        this.setState({image: image});
      });
      image.src = e.target.result;
    };
    reader.readAsDataURL(e.target.files[0]);
  }
}

function ExistingImagePanel(props) {
  return e('div', visibility(props.visible),
    e(StyledImagePlaceholder, {width: WIDTH})
  );
}

class ImageCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {activeTab: 'new'};
  }
  
  render() {
    return e(StyledCard, null,
      e(CardContent, null,
        e(Tabs, {
            variant: 'fullWidth',
            value: this.state.activeTab,
            onChange: (_, value) => this.setState({activeTab: value})},
          e(Tab, {value: 'new', label: 'New image'}),
          e(Tab, {value: 'existing', label: 'Existing image'})
        ),
        e(NewImagePanel, {
          imageCropper: this.props.imageCropper,
          visible: this.state.activeTab == 'new',
        }),
        e(ExistingImagePanel, {visible: this.state.activeTab == 'existing'})
      )
    );
  }
}

function MainContent(props) {
  return e('div', null,
    e(StyledMetadataCard, {
      title: props.title,
      subtitle: props.subtitle
    }),
    e(ImageCard, {imageCropper: props.imageCropper}),
    e(StyledDoneFab, {color: 'secondary'},
      e('i', {className: 'material-icons', onClick: e => props.onDone()}, 'done')
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
      activeImageTab: 'new',
      working: false,
      title: null,
      subtitle: null
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
        title: this.state.title,
        subtitle: this.state.subtitle,
        onDone: () => this.handleDone(),
        imageCropper: this.imageCropper,
      });
    }
    return e(MuiThemeProvider, {theme: theme},
      e(CssBaseline),
      e(MainAppBar),
      content
    );
  }
  
  handleDone() {
    const output = {
      type: 'NEW_IMAGE',
      title: this.state.title,
      subtitle: this.state.subtitle,
      //imageData: this.imageCropper.current.renderImage(),
      onUpdate: update => this.handleWorkingUpdate(update)
    };
    this.setState({working: true, workingMessage: 'Processing...'});
    this.props.onDone(output);
  }
  
  handleWorkingUpdate(update) {
    console.log(update);
    this.setState({workingMessage: update.message});
    console.log(this.state);
  }
}

return ThumbnailCreator;
})));