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
};

// Event listener for inter-component communication
var addPostEventlistener = {
  addPost: function(){
    if(this.listener){
      this.listener.addPost();
    }
  },
  listener: undefined
};

var ws = new Socket();

var Navigation = React.createClass({
  getInitialState: function(){
    return {
      username: undefined
    }
  },
  componentDidMount: function(){
    this.ws = new Socket();
    this.ws.target = this;
    this.ws.send('auth');
  },
  onmessage: function(e){
    var data = JSON.parse(e);
    if(data.username){
      this.setState({
        username: data.username
      });
    }
  },
  addPost: function(){
    addPostEventlistener.addPost();
  },
  render: function(){
    var loginLogoutLabel = this.state.username ? "Logout" : "Login";
    var loginLogoutLink = this.state.username ? "/logout/" : "/login/";
    var mainNav = this.state.username ? (
      <ul className="nav navbar-nav">
        <li className="nav-item">
          <a className="nav-link" href="#" onClick={this.addPost}>New Post</a>
        </li>
      </ul>
    ) : undefined;
    var loginInfo = this.state.username ? (
      <li className="nav-item">
        <span className="nav-text">Eingeloggt als {this.state.username}</span>
      </li>
    ) : undefined;
    return (
      <nav className="navbar navbar-fixed-top navbar-light bg-faded">
        <div className="container">
          <a className="navbar-brand" href="/">Skynet2</a>
          {mainNav}
          <ul className="nav navbar-nav pull-xs-right">
            {loginInfo}
            <li className="nav-item">
              <a className="nav-link" href={loginLogoutLink}>{loginLogoutLabel}</a>
            </li>
          </ul>
        </div>
      </nav>
    )
  }

});

var LikeButton = React.createClass({
    toggleLike: function(){
        ws.send('like', {
            post_id: this.props.postId,
            user_id: this.props.user_id
        });
    },
    render: function(){
        var like = this.props.likes.indexOf(this.props.user_id) > -1;
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

var NewPost = React.createClass({
    getInitialState: function(){
        return {
            text: ''
        }
    },
    handleSubmit: function(){
        ws.send('new_post', {
            user_id: this.props.user_id,
            text: this.state.text
        });
        this.props.onCancel();
    },
    handleText: function(e){
        var value = e.currentTarget.value;
        this.setState({text: value});        
    },
    render: function(){
        return (
            <div className="row post">
            <div className="col-md-8 col-md-offset-2">
            <div className="card">
            <form onSubmit={this.handleSubmit}>
                <div className="card-block">
                    <fieldset className="form-group">
                        <textarea
                            className="form-control"
                            rows="4"
                            placeholder="Ein neuer Post!"
                            onChange={this.handleText}
                        ></textarea>
                    </fieldset>
                    <button
                        type="button"
                        className="btn btn-warning"
                        onClick={this.props.onCancel}
                    >Cancel
                    </button>&nbsp;
                    <button type="submit" className="btn btn-primary">Submit</button>
                </div>
            </form>
            </div>
            </div>
            </div>
        )
    }
});

var PostList = React.createClass({
    getInitialState: function(){
        return {
            posts: [],
            user_id: undefined,
            addPost: false
        }
    },
    onmessage: function(e){
        var data = JSON.parse(e);
        console.log(data);
        if(data.posts){
            var posts = this.state.posts.concat(data.posts);
            console.log("Received " + data.posts.length + " posts.");
            console.log("New size is " + posts.length + " posts.");

            // Filter duplicates
            posts = posts.filter(function (e, i, arr) {
                var ids = arr.map(function(e){ return e.id; });
                return ids.lastIndexOf(e.id) === i;
            });
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
            for(var key in posts){
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
        };
        if(data.user_id){
            this.setState({user_id: data.user_id});
        };
    },
    componentDidMount: function(){
        addPostEventlistener.listener = this;
        ws.target = this;
        window.addEventListener('scroll', this.approachingBottom, false);
        ws.send('auth');
        this.loadPosts();
    },
    loadPosts: function(){
        var data = {
            offset: this.state.posts.length,
            rows: 10
        };
        console.log("Requesting " + data.rows + " new posts, starting from " + data.offset);
        ws.send('get_posts', data);
    },
    addPost: function(){
        this.setState({addPost: true});
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
            this.loading = true;
            this.loadPosts();
        }
    },
    cancelNewPost: function(){
        this.setState({addPost: false});
    },
    render: function(){
        var postViews = [];
        for(var key in this.state.posts){
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
                                    <LikeButton postId={post.id} likes={post.likes} user_id={this.state.user_id} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };
        var addPost = this.state.addPost
            ? <NewPost
                user_id={this.state.user_id}
                onCancel={this.cancelNewPost}
            />
            : '';
        return (
            <div>
                {addPost}
                {postViews}
            </div>
        );
    }
})

var postList = React.render(<PostList />, document.getElementById('posts-container'));
var navigation = React.render(<Navigation />, document.getElementById('navigation'));
