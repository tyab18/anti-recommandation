const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const srcPath = (...p) => path.join(__dirname, 'src', ...p);

module.exports = {
  // mode
  mode: process.env.prod ? 'production' : 'development',
  // main js file
  entry: {
    index: srcPath('index.ts'),
  },
  // converted file
  output: {
    filename: '[name].js',
  },
  // resolve
  resolve: {
    extensions: ['.ts', '.js', '.vue', '.json'],
    alias: {
      '@': path.resolve('src/vue'),
    },
  },
  // loader
  module: {
    rules: [
      {
        test: /\.ts$/,
        loader: 'ts-loader',
        exclude: /node_modules/,
        //* .vue
        options: {
          appendTsSuffixTo: [/\.vue$/],
        },
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {url: false},
          },
        ],
      },
    ],
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: srcPath('html/index.html'),
      title: '',
      filename: 'index.html',
      chunks: ['index'],
    }),
  ],
};
