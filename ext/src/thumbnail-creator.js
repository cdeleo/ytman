(function (global, factory) {
  global.ThumbnailCreator = factory();
}(this, (function () {

  const SCRYFALL_URL = 'https://api.scryfall.com/';
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
    Table,
    TableBody,
    TableCell,
    TableRow,
    TextField,
    Toolbar,
    Typography,
    createMuiTheme,
    withStyles
  } = window['material-ui'];

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
    return e(AppBar, { position: 'sticky' },
      e(Toolbar, null,
        e(Typography, { variant: 'h6', color: 'inherit' }, 'Generate thumbnail')
      )
    );
  }

  function MetadataCard(props) {
    const data = [
      { key: 'title', label: 'title', value: props.title },
      { key: 'subtitle', label: 'subtitle', value: props.subtitle },
    ];
    return e(StyledCard, null,
      e(CardContent, null,
        e(Table, null,
          e(TableBody, null,
            data.map(row =>
              e(TableRow, { key: row.key },
                e(TableCell, {
                  className: props.classes.cell,
                  style: { width: 100 }
                },
                  e(Typography, {
                    className: props.classes.label, variant: 'subtitle1'
                  },
                    row.label)
                ),
                e(TableCell, { className: props.classes.cell },
                  e(Typography, { variant: 'subtitle1' }, row.value)
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
      style: { width: props.width, height: height }
    });
  }

  const StyledImagePlaceholder = withStyles(theme => ({
    root: {
      marginTop: theme.spacing.unit,
      marginBottom: theme.spacing.unit,
      backgroundColor: theme.palette.grey[300],
    }
  }))(ImagePlaceholder);

  class ImageControls extends React.Component {
    constructor(props) {
      super(props);
      this.imageCropper = React.createRef();
      this.fileInput = React.createRef();
    }

    render() {
      let imageComponent;
      if (this.props.image.value) {
        imageComponent = e(ImageCropper, {
          ref: this.imageCropper,
          image: this.props.image.value,
          width: WIDTH
        });
      } else {
        imageComponent = e(StyledImagePlaceholder, { width: WIDTH });
      }
      return e('div', null,
        imageComponent,
        e('div', null,
          e(Button, {
            onClick: e => this.fileInput.current.click()
          }, 'select'),
          e(Button, {
            onClick: e => {
              if (this.imageCropper.current) {
                this.imageCropper.current.resetMask();
              }
            }
          }, 'reset')
        ),
        e('input', {
          ref: this.fileInput,
          style: { display: 'none' },
          type: 'file',
          accept: 'image/*',
          onChange: e => this.handleImageChange(e),
        }),
      );
    }

    handleImageChange(e) {
      if (e.target.files.length === 0) {
        this.props.image.onChange(null);
        return;
      }
      const reader = new FileReader();
      reader.onload = e => {
        const image = new Image();
        image.addEventListener('load', () => {
          this.props.image.onChange(
            image,
            () => this.imageCropper.current ? this.imageCropper.current.renderImage() : null
          );
        });
        image.src = e.target.result;
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  }

  class CardDataControls extends React.Component {
    render() {
      return e('div', null,
        e(StyledTextField, {
          label: 'multiverse id',
          fullWidth: true,
          value: this.props.mid.value || '',
          onChange: e => this.handleMidChange(e.target.value),
          onBlur: e => this.props.mid.onSubmit(e.target.value),
        }),
        e(StyledTextField, {
          label: 'name',
          fullWidth: true,
          value: this.getCardName(),
          InputProps: this.getNameInputProps(),
        }),
      );
    }

    handleMidChange(mid) {
      if (/^[0-9]*$/.test(mid)) {
        this.props.mid.onChange(mid);
      }
    }

    getCardName() {
      if (this.props.cardData && this.props.cardData.data) {
        return this.props.cardData.data.name;
      }
      return '';
    }

    getNameInputProps() {
      const props = { readOnly: true };
      if (this.props.cardData && this.props.cardData.loading) {
        props.startAdornment = e(InputAdornment, { position: 'end' },
          e(CircularProgress, { color: 'secondary', size: 20 })
        );
      }
      return props;
    }
  }

  function ImageCard(props) {
    return e(StyledCard, null,
      e(CardContent, null,
        e(ImageControls, { image: props.image }),
        e(CardDataControls, { mid: props.mid, cardData: props.cardData }),
      )
    );
  }

  class MainContent extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        title: null,
        subtitle: null,
        image: null,
        getImageData: null,
        mid: null,
        cardData: null,
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
        this.setState({ title: 'title', subtitle: 'subtitle' });
      }
    }

    render() {
      return e('div', null,
        e(StyledMetadataCard, {
          title: this.state.title,
          subtitle: this.state.subtitle
        }),
        e(ImageCard, {
          image: {
            value: this.state.image,
            onChange: (image, getImageData) =>
              this.setState({ image: image, getImageData: getImageData }),
          },
          mid: {
            value: this.state.mid,
            onChange: mid => this.handleMidChange(mid),
            onSubmit: mid => this.handleMidSubmit(mid),
          },
          cardData: this.state.cardData,
        }),
        e(StyledDoneFab, {
          color: 'secondary',
          disabled: !this.state.image,
          onClick: e => this.handleDone(),
        },
          e('i', { className: 'material-icons' }, 'done')
        )
      );
    }

    handleMidChange(mid) {
      this.setState({ mid: mid });
    }

    handleMidSubmit(mid) {
      const newState = { mid: mid };
      if (!this.state.cardData || this.state.cardData.forMid != mid) {
        if (mid) {
          console.log('Fetching card data for ' + mid);
          newState.cardData = { loading: true };
          fetch(SCRYFALL_URL + 'cards/multiverse/' + mid)
            .then(response => response.json())
            .then(cardData => this.setState(
              state => state.mid == mid ? {
                cardData: { forMid: mid, data: cardData }
              } : null
            ));
        } else {
          newState.cardData = null;
        }
      }
      this.setState(newState);
    }

    handleDone() {
      this.props.onDone({
        title: this.state.title,
        subtitle: this.state.subtitle,
        cardData: this.state.cardData ? this.state.cardData.data : null,
        getImageData: this.state.getImageData,
      });
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
    return e('div', { style: containerStyle },
      e('div', null,
        e(CircularProgress, { color: 'secondary', style: { margin: 16 } })
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
        workingMessage: '',
      };
    }

    render() {
      let content;
      if (this.state.working) {
        content = e(WorkingContent, { message: this.state.workingMessage });
      } else {
        content = e(MainContent, { onDone: output => this.handleDone(output) });
      }
      return e(MuiThemeProvider, { theme: theme },
        e(CssBaseline),
        e(MainAppBar),
        content
      );
    }

    handleDone(output) {
      this.setState({ working: true, workingMessage: 'Processing...' });
      this.props.onDone({
        ...output,
        onUpdate: update => this.setState({ workingMessage: update.message }),
      });
    }
  }

  return ThumbnailCreator;
})));