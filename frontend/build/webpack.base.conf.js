'use strict'
const path = require('path')
const utils = require('./utils')
const config = require('../config')
const vueLoaderConfig = require('./vue-loader.conf')
const { VueLoaderPlugin } = require('vue-loader') // <-- Obligatorio para Vue

function resolve (dir) {
  return path.join(__dirname, '..', dir)
}

module.exports = {
  context: path.resolve(__dirname, '../'),
  entry: {
    app: './src/main.js'
  },
  output: {
    path: config.build.assetsRoot,
    filename: '[name].js',
    publicPath: process.env.NODE_ENV === 'production'
      ? config.build.assetsPublicPath
      : config.dev.assetsPublicPath
  },
  resolve: {
    symlinks: false, // <-- Evita que Webpack se confunda con enlaces simbólicos
    extensions: ['.js', '.vue', '.json'],
    alias: {
      // <-- Forzamos a que TODO el proyecto use la misma copia exacta de Vue
      vue$: resolve('node_modules/vue/dist/vue.esm.js'),
      '@npm_team/space-vue-client$': resolve('node_modules/@npm_team/space-vue-client/dist/space-vue-client.es.js'),
      '@': resolve('src')
    },
    // <-- El arreglo de los polyfills (sustituye al antiguo bloque 'node')
    fallback: {
      dgram: false,
      fs: false,
      net: false,
      tls: false,
      child_process: false,
      setImmediate: false
    }
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: vueLoaderConfig
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: [resolve('src'), resolve('test'), resolve('node_modules/webpack-dev-server/client')]
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        type: 'javascript/auto', // <-- Evita duplicados de archivos en Webpack 5
        options: {
          limit: 10000,
          name: utils.assetsPath('img/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
        loader: 'url-loader',
        type: 'javascript/auto', // <-- Evita duplicados de archivos en Webpack 5
        options: {
          limit: 10000,
          name: utils.assetsPath('media/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        loader: 'url-loader',
        type: 'javascript/auto', // <-- Evita duplicados de archivos en Webpack 5
        options: {
          limit: 10000,
          name: utils.assetsPath('fonts/[name].[hash:7].[ext]')
        }
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin() // <-- Necesario a partir de vue-loader 15+
  ]
}
