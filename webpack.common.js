const path = require('path');
const packages = require('./package.json');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

let config = {
  stats: {
    children: false
  },
  entry: {
    app: './src/js/index.js',
  },
  output: {
    path: path.resolve(__dirname, 'static'),
    filename: 'js/[name].[contenthash:8].bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        // exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: ['@babel/plugin-proposal-class-properties']
          }
        }
      },
      {
        test: /\.scss$/,
        use: [
          { loader: MiniCssExtractPlugin.loader },
          { loader: 'css-loader' },
          { loader: 'postcss-loader',
            options: {
              plugins: [
                require('autoprefixer'),
                require('cssnano')
              ]
            }
          },
          { loader: 'sass-loader' }
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/app.[contenthash:8].css',
    }),
    new ManifestPlugin()
  ]
}

if (packages.dependencies && Object.keys(packages.dependencies).length > 0) {
  config.entry = {
    ...config.entry,
    vendor: Object.keys(packages.dependencies)
  }

  config.optimization = {
    ...config.optimization,
    splitChunks: {
      chunks: 'all',
      name: 'vendor',
      filename: 'js/[name].[chunkhash:8].bundle.js'
    }
  }
}

module.exports = config;