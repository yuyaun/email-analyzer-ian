const path = require('path');
const { VueLoaderPlugin } = require('vue-loader');
const Dotenv = require('dotenv-webpack');

// Pick environment-specific config file based on build mode
const envFile = process.env.NODE_ENV === 'production' ? '.env.prod' : '.env.dev';

module.exports = {
  entry: './src/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    clean: true,
    publicPath: '/',
  },
  devServer: {
    static: path.resolve(__dirname, 'public'),
    hot: true,
    open: true,
    port: 8080,
  },
  module: {
    rules: [
      { test: /\.vue$/, loader: 'vue-loader' },
      { test: /\.js$/, loader: 'babel-loader', exclude: /node_modules/ },
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader', 'postcss-loader'],
      }
    ],
  },
  plugins: [
    new VueLoaderPlugin(),
    new Dotenv({ path: path.resolve(__dirname, envFile) }),
  ],
  resolve: {
    alias: {
      vue: 'vue/dist/vue.esm-bundler.js'
    },
    extensions: ['.js', '.vue']
  }
};