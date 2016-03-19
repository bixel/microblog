const webpack = require('webpack');
const autoprefixer = require('autoprefixer');

module.exports ={
  entry: [
    'tether',
    './static/js/script'
  ],
  output: {
    path: 'static/js/bundle',
    filename: 'app.js'
  },
  devtool: 'source-map',
  plugins: [
    new webpack.ProvidePlugin({
      "window.Tether": "tether"
    }),
    new webpack.ProvidePlugin({
        $: "jquery",
        jQuery: "jquery"
    })
  ],
  module: {
    loaders: [
      {
        test: /\.css$/,
        loaders: ['style', 'css', 'postcss']
      },
      {
        test: /\.scss$/,
        loaders: ['style', 'css', 'postcss', 'sass']
      },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        // Limiting the size of the woff fonts breaks font-awesome ONLY for the extract text plugin
        // loader: "url?limit=10000"
        loader: "url"
      },
      {
        test: /\.(ttf|eot|svg)(\?[\s\S]+)?$/,
        loader: 'file'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        query: {
          presets: ['es2016', 'react']
        }
      },
    ]
  },
  postcss: [autoprefixer],
};
