const path = require('path');

module.exports = {
  entry: './static/js/livekit-client.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static/dist'),
  },
  mode: 'development',
  resolve: {
    extensions: ['.js'],
  },
};