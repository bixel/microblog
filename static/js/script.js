var user_id = 1;

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

var LikeButton = React.createClass({
    toggleLike: function(){
        var likes = this.props.likes;
        if(likes.indexOf(user_id) > -1){
            likes.splice(likes.indexOf(user_id), 1);
        } else {
            likes.push(user_id);
        }
        this.props.likes = likes;
        ws.send('like', {
            post_id: this.props.postId,
            user_id: user_id
        });
    },
    render: function(){
        var like = this.props.likes.indexOf(user_id) > -1;
        var classes = React.addons.classSet({
            'btn btn-sm': true,
            'btn-primary': like,
            'btn-primary-outline': !like
        });
        var number = this.props.likes.length || '';
        return(
            <a
                className={classes}
                onClick={this.toggleLike}
                >
                &hearts; {number}
            </a>
        )
    }
});

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
            if(data.posts.length >= 10){
                this.loading = false;
            } else {
                this.reachedLastPage = true;
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
        if(data.like){
            var posts = this.state.posts;
            for(key in posts){
                var p = posts[key];
                if(p.id === data.like.post_id){
                    if(p.likes.indexOf(data.like.user_id) > -1 && !data.like.state){
                        p.likes.splice(p.likes.indexOf(data.like.user_id), 1);
                    } else if(p.likes.indexOf(data.like.user_id) < 0 && data.like.state) {
                        p.likes.push(data.like.user_id);
                    }
                    this.setState({
                        posts: posts
                    });
                    return;
                }
            }
        }
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
        ws.send('get_page', data);
    },
    loading: false,
    reachedLastPage: false,
    approachingBottom: function(e){
        var scrollPosition = window.pageYOffset;
        var windowSize     = window.innerHeight;
        var bodyHeight     = document.body.scrollHeight;
        var distanceBottom = bodyHeight - (scrollPosition + windowSize);
        if(distanceBottom < 300 && !this.loading && !this.reachedLastPage){
            console.log('Loading');
            this.loadPosts();
            this.loading = true;
        }
    },
    render: function(){
        var postViews = [];
        for(key in this.state.posts){
            var post = this.state.posts[key];
            var title = post.title;
            var img = <div className="img">{post.image}</div>;
            var created = new Date(post.created);
            postViews.push(
                <div className="row post" key={key}>
                    <div className="col-md-8 col-md-offset-2">
                        <div className="card">
                            <div className="card-header text-right text-muted">
                                #{post.id} {created.toLocaleString()} von {post.author.displayname}
                            </div>
                            {img}
                            <div className="card-block">
                                <p>{post.text}</p>
                                <div className="buttons">
                                    <LikeButton postId={post.id} likes={post.likes} />
                                </div>
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
                {postViews}
            </div>
        );
    }
})

React.render(<PostList />, document.getElementById('posts-container'));

