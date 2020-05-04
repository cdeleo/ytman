(function () {
    const e = React.createElement;
    const LIFESPAN_MS = 20000;

    class SidebarGenerator {

        static ALPHABET = 'abcdfgijklmnopqz0';

        // Fisher-Yates shuffle adapted from stackoverflow.com/a/6274381.
        static shuffle(a, rng) {
            var j, x, i;
            for (i = a.length - 1; i > 0; i--) {
                j = Math.floor(rng.uniform() * (i + 1));
                x = a[i];
                a[i] = a[j];
                a[j] = x;
            }
            return a;
        }

        static get(seed) {
            const rng = new RNG(seed);
            let r = '';
            while (r.length < 50) {
                const pool = Array.from(this.ALPHABET);
                SidebarGenerator.shuffle(pool, rng);
                r += pool.join('');
            }
            return r;
        }
    }

    function Message(props) {
        return e('div', { className: 'message' },
            e('div', { className: 'sidebar' }, SidebarGenerator.get(props.id)),
            e('span', { className: 'author' }, props.author),
            e('span', { className: 'text' }, props.message)
        );
    }

    function MessageList(props) {
        return e('div', { className: 'message-list' },
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
            this.props.fetchMessages.then(fetchMessages => this.fetchNew(fetchMessages));
        }

        render() {
            return e('div', { className: 'chat-log' },
                e(MessageList, { messages: this.state.messages })
            );
        }

        setFetchTimeout(fetchMessages, delay) {
            if (this.fetchTimer) {
                clearTimeout(this.fetchTimer);
            }
            this.fetchTimer = setTimeout(() => this.fetchNew(fetchMessages), delay);
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

        fetchNew(fetchMessages) {
            fetchMessages(this.state.token).then(r => {
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
                this.setFetchTimeout(fetchMessages, r.nextUpdateMs);
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
        gapi.client.setApiKey(new URLSearchParams(window.location.search).get('apikey'));
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

    function simulateFetchMessages(token) {
        const currentTime = Date.now();
        return Promise.resolve({
            newMessages: [
                { id: 'abc' + currentTime, author: 'octopus', message: 'hello there', timestamp: currentTime - 500 },
                { id: 'def' + currentTime, author: 'Pangolin', message: 'sick deck, bruh', timestamp: currentTime },
                { id: 'ghi' + currentTime, author: 'quetzel', message: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', timestamp: currentTime },
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

    function fetchMessages(chatId, token) {
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

    function getFetchMessages() {
        return new Promise(resolve => gapi.load('client', resolve))
            .then(() => loadClient())
            .then(() => getChatId(getVideoId()))
            .then(chatId => token => fetchMessages(chatId, token))
            .catch(err => {
                console.error(err);
                return simulateFetchMessages;
            });
    }

    ReactDOM.render(e(ChatLog, { fetchMessages: getFetchMessages() }), document.querySelector('#chat'));
})();