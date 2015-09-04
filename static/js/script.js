function Socket(){
    this.socket = io.connect('http://' + document.domain + ':' + location.port);
    this.socket.onopen = function(){
        console.log('Connected.');
    };
    this.socket.on('message', function(e){
        if(this.target){
            this.target.onmessage(e);
        } else {
            console.log('Received message, but no target is defined.');
        };
    }.bind(this));
    this.socket.on('close', function(){
        console.log('Socket will close');
    });
    this.send = function(event, data){
        this.socket.emit(event, data);
    };
}

var ws = new Socket();

var PostList = React.createClass({
    getInitialState: function(){
        return {
            posts: []
        }
    },
    onmessage: function(e){
        var data = JSON.parse(e);
        if(data.posts){
            var posts = this.state.posts.concat(data.posts);
            this.setState({posts: posts});
            console.log({received: data.posts.length});
            if(data.posts.length >= 10){
                this.loading = false;
            }
        };
        if(data.post){
            var posts = this.state.posts;
            var index = 0;
            while(data.post.id < this.state.posts[index].id){
                index++;
            }
            posts.unshift(data.post);
            this.setState({posts: posts});
        };
    },
    componentDidMount: function(){
        ws.target = this;
        window.addEventListener('scroll', this.approachingBottom, false);
    },
    loadPosts: function(){
        var data = {
            page: Math.floor(this.state.posts.length / 10) + 1,
            rows: 10
        };
        console.log(data);
        ws.send('get_page', data);
    },
    loading: false,
    approachingBottom: function(e){
        var scrollPosition = window.pageYOffset;
        var windowSize     = window.innerHeight;
        var bodyHeight     = document.body.scrollHeight;
        var distanceBottom = bodyHeight - (scrollPosition + windowSize);
        if(distanceBottom < 300 && !this.loading){
            this.loadPosts();
            this.loading = true;
        }
    },
    render: function(){
        var posts = [];
        for(key in this.state.posts){
            var post = this.state.posts[key];
            var title = post.title;
            var img = <div className="img">{post.image}</div>;
            var created = new Date(post.created);
            posts.push(
                <div className="row post" key={key}>
                    <div className="col-md-8 col-md-offset-2">
                        <div className="card">
                            <div className="card-header text-right text-muted">
                                #{post.id} {created.toLocaleString()} von {post.author.displayname}
                            </div>
                            {img}
                            <div className="card-block">
                                <p>{post.text}</p>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };
        var addPost = function(){
            ws.send('new_post', {
                user_id: 1,
                text: 'Yaaaay a random text.'
            });
        };
        return (
            <div>
                <button onClick={this.loadPosts}>
                    Load Posts
                </button>
                <button onClick={addPost}>
                    Add Post
                </button>
                {posts}
            </div>
        );
    }
})

React.render(<PostList />, document.getElementById('posts-container'));

