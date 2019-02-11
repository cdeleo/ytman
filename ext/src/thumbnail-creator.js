(function (global, factory) {
  global.ThumbnailCreator = factory();
}(this, (function() {

const APP_ID = 'backend-dot-youtube-manager-196811';

const e = React.createElement;

const {
  AppBar,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
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
  const height = Math.round(props.width * 720 / 1280);
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
        width: 400
      });
    } else {
      imageComponent = e(StyledImagePlaceholder, {width: 400});
    }
    return e('div', visibility(this.props.visible),
      imageComponent,
      e('div', null,
        e(Button, {
            onClick: e => this.fileInput.current.click()}, 'select'),
        e(Button, {
            onClick: e => this.props.imageCropper.current.resetMask()}, 'reset')
      ),
      e(StyledTextField, {label: 'name', required: true, fullWidth: true}),
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
    e(StyledImagePlaceholder, {width: 400})
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

class ThumbnailCreator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {activeImageTab: 'new', title: null, subtitle: null};
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
    return e(MuiThemeProvider, {theme: theme},
      e(CssBaseline),
      e(MainAppBar),
      e(StyledMetadataCard, {
        title: this.state.title,
        subtitle: this.state.subtitle
      }),
      e(ImageCard, {imageCropper: this.imageCropper}),
      e(StyledDoneFab, {color: 'secondary'},
        e('i', {className: 'material-icons'}, 'done')
      )
    );
  }
  
  handleDone() {
    console.log(this.imageCropper.current.renderImage());
  }
}

return ThumbnailCreator;
})));