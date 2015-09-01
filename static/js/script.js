var PostList = React.createClass({
    getInitialState: function(){
        return {
            posts: []
        }
    },
    componentDidMount: function(){
        $.getJSON('/api/posts/', function(data){
            this.setState({
                posts: data.posts
            })
        }.bind(this))
        .fail(function(data){
            console.log(data);
        });
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
                    <div className="col-md-12">
                        <div className="card">
                            <div className="card-header text-right text-muted">
                                {created.toLocaleString()} von {post.author.displayname}
                            </div>
                            {img}
                            <div className="card-block">
                                <p>{post.text}</p>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }
        return (
            <div>{posts}</div>
        );
    }
})

React.render(<PostList />, document.getElementById('posts-container'));
