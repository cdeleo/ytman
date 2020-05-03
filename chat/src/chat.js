const e = React.createElement;
const API_KEY = 'AIzaSyC83lskLDWEWCWvfoc0qKpl_cxEHMJrRok';
const LIFESPAN_MS = 20000;

function Message(props) {
    return e('div', null, props.author + ': ' + props.message);
}

function MessageList(props) {
    return e('div', null,
        props.messages.map(m => e(Message, { ...m, key: m.id }))
    );
}

class ChatLog extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            token: null,
            messages: []
        };
        this.fetchTimer = null;
        this.expireTimer = null;
    }

    componentDidMount() {
        this.fetchNew();
    }

    render() {
        return e(MessageList, { messages: this.state.messages });
    }

    setFetchTimeout(delay) {
        if (this.fetchTimer) {
            clearTimeout(this.fetchTimer);
        }
        this.fetchTimer = setTimeout(() => this.fetchNew(), delay);
    }

    setExpireTimeout(messages) {
        if (this.expireTimer) {
            clearTimeout(this.expireTimer);
            this.expireTimer = null;
        }
        if (messages.length) {
            this.expireTimer = setTimeout(() => this.expireOld(), messages[0].timestamp + LIFESPAN_MS - Date.now());
        }
    }

    fetchNew() {
        this.props.fetchMessages(this.state.token).then(r => {
            this.setState(state => {
                const currentTime = Date.now();
                const newMessages = r.newMessages
                    .filter(m => m.timestamp + LIFESPAN_MS > currentTime)
                    .sort((a, b) => a.timestamp - b.timestamp);
                const totalMessages = [...state.messages, ...newMessages];
                this.setExpireTimeout(totalMessages);
                return {
                    token: r.token,
                    messages: totalMessages,
                };
            });
            this.setFetchTimeout(r.nextUpdateMs);
        });
    }

    expireOld() {
        this.setState(state => {
            const expirationTime = Date.now() - LIFESPAN_MS;
            const totalMessages = state.messages.filter(m => m.timestamp > expirationTime);
            this.setExpireTimeout(totalMessages);
            return { messages: totalMessages };
        });
    }
}

function loadClient() {
    gapi.client.setApiKey(API_KEY);
    return gapi.client.load('https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest');
}

function getVideoId() {
    return new URLSearchParams(window.location.search).get('v');
}

function getChatId(videoId) {
    return gapi.client.youtube.videos.list({
        'part': 'liveStreamingDetails',
        'id': videoId,
    }).then(r => {
        if (r.result.items.length) {
            return r.result.items[0].liveStreamingDetails.activeLiveChatId;
        } else {
            throw new Error('Video ' + videoId + ' not found.');
        }
    });
}

let chatId = null;

function startChat() {
    loadClient()
        .then(() => getChatId(getVideoId()))
        .then(r => { chatId = r; });
}

function simulateFetchMessages(token) {
    const currentTime = Date.now();
    return Promise.resolve({
        newMessages: [
            { id: 'abc' + currentTime, author: 'octopus', message: 'hello there ' + currentTime, timestamp: currentTime - 500 },
            { id: 'def' + currentTime, author: 'pangolin', message: 'sick deck, bruh ' + currentTime, timestamp: currentTime },
        ],
        token: token + 1,
        nextUpdateMs: 1000,
    });
}

function convertToMessage(item) {
    return {
        id: item.id,
        author: item.authorDetails.displayName,
        message: item.snippet.displayMessage,
        timestamp: Date.parse(item.snippet.publishedAt),
    };
}

function actuallyFetchMessages(token) {
    const request = {
        liveChatId: chatId,
        part: "id,snippet,authorDetails",
    };
    if (token) {
        request.pageToken = token;
    }
    return gapi.client.youtube.liveChatMessages.list(request).then(
        r => {
            const messages = r.result.items
                .filter(item => item.snippet.type == 'textMessageEvent')
                .map(item => convertToMessage(item));
            return {
                newMessages: messages,
                token: r.result.nextPageToken,
                nextUpdateMs: r.result.pollingIntervalMillis,
            }
        }
    );
}

function fetchMessages(token) {
    if (chatId) {
        return actuallyFetchMessages(token);
    } else {
        return Promise.resolve({ newMessages: [], token: null, nextUpdateMs: 1000 });
    }
}

gapi.load('client', startChat);
ReactDOM.render(e(ChatLog, { fetchMessages: fetchMessages }), document.querySelector('#chat'));