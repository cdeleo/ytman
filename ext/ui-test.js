const APP_ID = 'backend-dot-youtube-manager-196811';
const TOKEN = 'ya29.GlylBqi8SaXeH9IjT5j5Up89DYXP0J5Kk6rGGo8hnATXhSwWtsFTWT3X5dcnAC97L8R9KXSVmziE1VYaRsD0qAffVFEHnlpA8SHF-svRrqGibo6oYSSzOIn_O6cnsA';

const TEST_IMAGES = [
  {key: 'o', name: 'octopus'},
  {key: 'p', name: 'pangolin'},
  {key: 'q', name: 'quetzal'},
];

const e = React.createElement;

const {
  Button,
  ExpansionPanel,
  ExpansionPanelDetails,
  ExpansionPanelSummary,
  Typography
} = window['material-ui'];

function apiUrl(appId, api, version, method) {
  return `https://${appId}.appspot.com/_ah/api/${api}/${version}/${method}`;
}

class NewImagePanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {image: null};
    this.fileInput = React.createRef();
  }
  
  render() {
    return e(ExpansionPanel, {expanded: this.props.expanded, onChange: this.props.onChange},
        e(ExpansionPanelSummary, null,
            e(Typography, null, 'New image')
        ),
        e(ExpansionPanelDetails, null,
            e('div', null,
                e(ImageCropper, {
                    ref: this.props.imageCropper,
                    image: this.state.image,
                    width: 400
                }, null),
                e('div', null,
                  e(Button, {
                      onClick: e => this.fileInput.current.click()
                  }, 'select'),
                  e(Button, {
                      onClick: e => this.props.imageCropper.current.resetMask()
                  }, 'reset')
                ),
                e('input', {
                    ref: this.fileInput,
                    style: {display: 'none'},
                    type: 'file',
                    accept: 'image/*',
                    onChange: e => this.handleImageChange(e)
                })
            )
        )
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
  return e(ExpansionPanel, {expanded: props.expanded, onChange: props.onChange},
      e(ExpansionPanelSummary, null,
          e(Typography, null, 'Existing image')
      ),
      e(ExpansionPanelDetails, null,
          'existing'
      )
  );
}

class ThumbnailCreator extends React.Component {
  constructor(props) {
    super(props);
    //this.state = {images: []};
    this.state = {activeImageTab: 'new'};
    this.imageCropper = React.createRef();
  }
  
  componentDidMount() {
    // const options = {headers: {Authorization: 'Bearer ' + TOKEN}};
    // fetch(apiUrl(APP_ID, 'ytman', 'v1', 'images/list'), options)
    //   .then(res => res.json())
    //   .then(res => this.setState({images: res.images ? res.images : null}));
    //this.setState({images: TEST_IMAGES});
  }
  
  render() {
    return e('div', null,
        e(NewImagePanel, {
            ...this.imagePanelProps('new'),
            imageCropper: this.imageCropper
        }),
        e(ExistingImagePanel, this.imagePanelProps('existing')),
        e(Button, {onClick: e => this.handleDone()}, 'done')
    );
  }
  
  imagePanelProps(key) {
    return {
      key: key,
      expanded: this.state.activeImageTab == key,
      onChange: (_, expanded) => this.setState(
          {activeImageTab: expanded ? key : null}),
    };
  }
  
  handleDone() {
    console.log(this.imageCropper.current.renderImage());
  }
}

const imageList = e(ThumbnailCreator);
ReactDOM.render(imageList, document.querySelector('#image-list'));